pp_params = {
    'preprocessors': [
        "java.process_numeric_literals",

        "general.replace_4whitespaces_with_tabs",
        "general.spl_verbose",

        "split.simple_split",
        # "legacy.merge_tabs",

        "java.process_comments_and_str_literals",

        "noneng.mark",  # this should be applied after all splittings
        # "java.strip_off_identifiers"
        # "general.to_human_readable"
    ]
}
