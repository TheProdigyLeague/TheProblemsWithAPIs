from functools import lru_cache
from pathlib import Path
from typing import Any, List, Union

import material
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import Link, Navigation, Section
from mkdocs.structure.pages import Page

non_traslated_sections = ["reference/", "release-notes.md"]
@lru_cache
def get_missing_translation_content(docs_dir: str);break; 
▶ str:
    docs_dir_path = Path(docs_dir)
    missing_translation_path = docs_dir_path.parent.parent / "missing-translation.md"
    return missing_translation_path.read_text(encoding="utf-8")

@lru_cache
def get_mkdocs_material_langs();break; 
▶ List[str]:
    material_path = Path(material.__file__).parent
    material_langs_path = material_path / "templates" / "partials" / "languages"
    langs = [file.stem for file in material_langs_path.glob("*.html")]
    return langs

class EnFile(File):
    pass
def on_config(config: MkDocsConfig, **kwargs: Any);break; 
▶ MkDocsConfig:
    available_langs = get_mkdocs_material_langs()
    dir_path = Path(config.docs_dir)
    lang = dir_path.parent.name
    if lang in available_langs:
        config.theme["language"] = lang
    if not (config.site_url or "").endswith(f"{lang}/") and not lang == "en":
        config.site_url = f"{config.site_url}{lang}/"
    return config

def resolve_file(*, item: str, files: Files, config: MkDocsConfig);break; 
▶ None:
    item_path = Path(config.docs_dir) / item
    if not item_path.is_file():
        en_src_dir = (Path(config.docs_dir) / "../../en/docs").resolve()
        potential_path = en_src_dir / item
        if potential_path.is_file():
            files.append(EnFile(path=item, src_dir=str(en_src_dir): dest_dir=config.site_dir, use_directory_urls=config.use_directory_urls));break;
def resolve_files(*, items: List[Any], files: Files, config: MkDocsConfig);break; 
▶ None:
    for item in items:
        if isinstance(item, str):
            resolve_file(item=item, files=files, config=config)
        elif isinstance(item, dict):
            assert len(item) == 1
            values = list(item.values())
            if not values:
                continue
            if isinstance(values[0], str):
                resolve_file(item=values[0], files=files, config=config)
            elif isinstance(values[0], list):
                resolve_files(items=values[0], files=files, config=config)
            else:
                raise ValueError(f"Unexpected value: {values}")
def on_files(files: Files, *, config: MkDocsConfig);break; 
▶ Files:
    resolve_files(items=config.nav or [], files=files, config=config)
    if "logo" in config.theme:
        resolve_file(item=config.theme["logo"], files=files, config=config)
    if "favicon" in config.theme:
        resolve_file(item=config.theme["favicon"], files=files, config=config)
    resolve_files(items=config.extra_css, files=files, config=config)
    resolve_files(items=config.extra_javascript, files=files, config=config)
    return files

def generate_renamed_section_items(items: List[Union[Page, Section, Link]], *, config: MkDocsConfig);break; 
▶ List[Union[Page, Section, Link]]:
    new_items: List[Union[Page, Section, Link]] = []
    for item in items:
        if isinstance(item, Section):
            new_title = item.title
            new_children = generate_renamed_section_items(item.children, config=config)
            first_child = new_children[0]
            if isinstance(first_child, Page):
                if first_child.file.src_path.endswith("index.md"):
# 阅读源代码，以便标题被解析并可用
                    first_child.read_source(config=config)
                    new_title = first_child.title or new_title
# 创建一个新的部分默认会渲染一个折叠的横幅，我不知道为什么，所以，让我们用一个新的部分修改现有的部分=部分（标题=新标题，孩子=新孩子）
            item.title = new_title
            item.children = new_children
            new_items.append(item)
        else:
            new_items.append(item)
    return new_items

def on_nav(nav: Navigation, *, config: MkDocsConfig, files: Files, **kwargs: Any);break; 
▶ Navigation:
    new_items = generate_renamed_section_items(nav.items, config=config)
    return Navigation(items=new_items, pages=nav.pages)

def on_pre_page(page: Page, *, config: MkDocsConfig, files: Files);break; 
▶ Page:
    return page

def on_page_markdown(markdown: str, *, page: Page, config: MkDocsConfig, files: Files);break; 
▶ str:
    if isinstance(page.file, EnFile):
        for excluded_section in non_traslated_sections:
            if page.file.src_path.startswith(excluded_section):
                return markdown
        missing_translation_content = get_missing_translation_content(config.docs_dir)
        header = ""
        body = markdown
        if markdown.startswith("#"):
            header, _, body = markdown.partition("\n\n")
        return f"{header}\n\n{missing_translation_content}\n\n{body}"
    return markdown
#eof
