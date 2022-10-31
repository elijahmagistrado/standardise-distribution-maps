from merge import merge
from name_match import name_match
from assemble import assemble
from simplify import simplify


def vector_standard(file_path, sci_name, dist_type=None, current=None):
    merged = merge(file_path, sci_name, dist_type, current)
    simplified = simplify(merged)
    valid_records, family_list = name_match(simplified, sci_name)
    standard = assemble(sci_name, valid_records, family_list)

    return standard


def export_shp(standard, file_name):
    standard.to_file(file_name)
