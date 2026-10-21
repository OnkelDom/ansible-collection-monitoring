from pathlib import Path
import importlib.util


def test_mapping_methods_do_not_trigger_fact_collection():
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location('scaffold_mapping_test', root / 'tools/generate_role_scaffold.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    config = module.load_config()
    for role in module.iter_role_dirs():
        preflight = module.build_preflight(config, role.name)
        assert "'get'" not in preflight
        assert "'keys'" not in preflight


def test_bracket_fact_access_is_collected_when_missing(tmp_path):
    import sys
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location('scaffold_bracket_test', root / 'tools/generate_role_scaffold.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    role = tmp_path / 'sample'
    (role / 'tasks').mkdir(parents=True)
    (role / 'tasks/configuration.yml').write_text("value: \"{{ ansible_facts['python']['executable'] }}\"\n")
    module.ROLES_DIR = tmp_path
    assert "'python'" in module.build_preflight(module.load_config(), 'sample')
