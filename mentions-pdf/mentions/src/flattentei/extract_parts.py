from copy import deepcopy
from collections import defaultdict
from itertools import chain
import re


def get_units(ent_type, doc, doc_id=None, enrich_container=[]):
    relation_layer = "Scholarly"
    doc = deepcopy(doc)
    lines = generate_line_annos(doc["text"])
    doc["annotations"]["Line"] = lines
    units = list(get_ents(ent_type, doc["text"], doc["annotations"], doc_id))
    for unit in units:
        # reformat begin and end
        unit["begin"] = unit["begin_in_doc"]
        unit["end"] = unit["end_in_doc"]
        del unit["begin_in_doc"]
        del unit["end_in_doc"]
        container_dict = {}
        for container in unit["container"]:
            if container["type"] in enrich_container:
                begin = container["begin_in_doc"]
                end = container["end_in_doc"]
                container["text"] = doc["text"][begin:end]
            if container["type"] in container:
                raise Exception("More than one container of one type")
            container_dict[container["type"]] = container
        unit["container"] = container_dict
    add_relations(units, doc.get("relations", {}).get("Scholarly"))
    return units


def add_relations(units, relations):
    if not relations:
        return
    # match with annotations of units
    source_ent_relations = defaultdict(list)
    target_ent_relations = defaultdict(list)
    for relation_idx, relation in enumerate(relations):
        relation["idx"] = relation_idx
        source_ent_relations[relation["source_id"]].append(relation_idx)
        target_ent_relations[relation["target_id"]].append(relation_idx)

    for unit in units:
        ent_ids = {a.get("ref_id") for a in unit["annotations"] if "ref_id" in a}

        relations_idxs_source = set(
            chain(*[source_ent_relations[e_id] for e_id in ent_ids])
        )
        relations_idxs_target = set(
            chain(*[target_ent_relations[e_id] for e_id in ent_ids])
        )
        relations_idxs_inner = relations_idxs_source & relations_idxs_target
        units_relations = [
            deepcopy(relations[i])
            for i in list(relations_idxs_source | relations_idxs_target)
        ]
        for rel in units_relations:
            rel["source_in_unit"] = rel["idx"] in relations_idxs_source
            rel["target_in_unit"] = rel["idx"] in relations_idxs_target
            rel["inner"] = rel["idx"] in relations_idxs_inner
        unit["relations"] = units_relations
    # match with unit itself
    # @todo


def get_ents(ent_type, text, annos, doc_id=None):
    other_ents = [k for k in annos.keys() if k != ent_type]
    left_annos = deepcopy({k: v[::-1] for k, v in annos.items() if k != ent_type})
    for ent in annos.get(ent_type, []):
        ent_info = {k: v for k, v in ent.items()}
        ent_info["type"] = ent_type
        ent_info["text"] = text[ent["begin"] : ent["end"]]
        begin, end = ent["begin"], ent["end"]
        found_ents = update_left_annos(left_annos, begin, end)
        found_ents = list(found_ents)
        container_ents = [
            e for e, ent_flag in found_ents if ent_flag == "container_ent"
        ]
        # sort container by size (biggest (most genral) first)
        container_ents.sort(key=lambda x: -x["end_in_doc"] + x["begin_in_doc"])
        sub_ents = [e for e, ent_flag in found_ents if ent_flag == "sub_ent"]
        overlapping_ents = [
            e for e, ent_flag in found_ents if ent_flag == "overlapping_ent"
        ]
        ent_info["annotations"] = sub_ents
        ent_info["container"] = container_ents
        if overlapping_ents:
            ent_info["annotations_overlap"] = overlapping_ents
        ent_info["begin_in_doc"] = ent_info["begin"]
        del ent_info["begin"]
        ent_info["end_in_doc"] = ent_info["end"]
        del ent_info["end"]
        if doc_id is not None:
            ent_info["doc_id"] = doc_id
        yield ent_info


def update_left_annos(left_annos, begin, end):
    for key, values in left_annos.items():
        while True:
            if not values:
                break
            next_ent = values[-1]
            if next_ent["end"] <= begin:
                # span is before
                values.pop()
                continue
            elif next_ent["begin"] <= begin and next_ent["end"] >= end:
                # span is container span of this span
                next_ent["begin_in_doc"] = next_ent["begin"]
                next_ent["end_in_doc"] = next_ent["end"]
                next_ent["offset_to_container"] = begin - next_ent["begin_in_doc"]
                # next_ent["end_in_container"] = end - next_ent["begin_in_doc"]
                next_ent["type"] = key
                without_begin_end = deepcopy(next_ent)
                del without_begin_end["begin"]
                del without_begin_end["end"]
                yield without_begin_end, "container_ent"
                break
            elif next_ent["begin"] >= end:
                # span is after
                break
            elif next_ent["begin"] >= begin and next_ent["end"] <= end:
                # span is sub span of this span
                next_ent = values.pop()
                next_ent["begin_in_doc"] = next_ent["begin"]
                next_ent["end_in_doc"] = next_ent["end"]
                next_ent["begin"] -= begin
                next_ent["end"] -= begin
                next_ent["type"] = key
                yield next_ent, "sub_ent"
            else:
                # no container and no subspan => span has an overlap!
                if end >= next_ent["end"]:
                    values.pop()
                yield next_ent, "overlapping_ent"
                break


line_pattern = re.compile("[^\n]*[\n$]")


def generate_line_annos(text):
    lines = []
    for idx, line in enumerate(line_pattern.finditer(text)):
        if line.group().strip():
            lines.append(dict(begin=line.start(), end=line.end(), idx=idx))
    return lines
