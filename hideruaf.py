from typing import Any
import unreal

# 测试


def test():
    """
    测试脚本是否加载成功，成功输出pass

    """
    print("pass")


# 饺子


def process_path_str(dir_path: str) -> str:
    """对路径进行处理，如果不以/开头，加上，如果不是根路径开头，选定内容为根路径

    Args:
        dir_path (str): 原始路径

    Returns:
        str: 处理后的路径
    """
    if not dir_path.startswith("/"):
        dir_path = "/" + dir_path
    if not (
        dir_path.startswith("/Game")
        or dir_path.startswith("/Classes_Game")
        or dir_path.startswith("/EngineData")
    ):
        dir_path = "/Game" + dir_path
    return dir_path


def does_dir_exist(dir_path: str) -> bool:
    """判断文件夹路径是否存在，若没有指定根目录['/Game','/Classes_Game','/EngineData'],则默认为'/Game'目录，即内容

    Args:
        dir_path (str): 路径
    """
    dir_path = process_path_str(dir_path)
    return unreal.EditorAssetLibrary.does_directory_exist(dir_path)


def create_dir(dir_path: str):
    """新建文件夹（不做指定的话默认内容目录）

    Args:
        dir_path (str): 路径

    Returns:
        bool: _description_
    """
    if not does_dir_exist(dir_path):
        dir_path = process_path_str(dir_path)
        unreal.EditorAssetLibrary.make_directory(dir_path)
        print(f'create directory {dir_path.split("/")[-1]} success')
    else:
        print("directory aleardy exists")


def delete_dir(dir_path: str):
    """删除目录（不做指定的话默认内容目录）

    Args:
        dir_path (str): 路径

    Returns:
        bool: 执行结果
    """
    dir_path = process_path_str(dir_path)
    return unreal.EditorAssetLibrary.delete_directory(dir_path)


def rename_dir(dir_path: str):
    """重命名文件夹

    Args:
        dir_path (str): 路径
    """
    dir_path = process_path_str(dir_path)
    unreal.EditorAssetLibrary.rename_directory(dir_path)


def move_asset(source_asset_path: str, destination_asset_path: str):
    """重命名文件，当做移动用

    Args:
        source_asset_path (str): 源路径
        destination_asset_path (str): 目标路径
    """
    unreal.EditorAssetLibrary.rename_asset(source_asset_path, destination_asset_path)


def copy_file_to(original_file: str, target_path: str, new_name: str = None):
    """复制文件到指定文件夹，可重命名

    Args:
        source_path (str): 原路径
        target_path (str): 目标路径
        new_name (str, optional): 新名字. Defaults to None.
    """
    original_file = process_path_str(original_file)
    target_path = process_path_str(target_path)
    if unreal.EditorAssetLibrary.does_asset_exist(original_file):
        if new_name is None:
            new_name = original_file.split("/")[-1]
        unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(
            asset_name=new_name,
            package_path=target_path,
            original_object=unreal.load_asset(original_file),
        )
        print(f'迁移{original_file.split("/")[-1]}至{target_path}成功，名字为{new_name}')
    else:
        print("目标文件不存在")


def get_selected_assets():
    """获取选中的资产，返回资产路径

    Returns:
        list[object]: _description_
    """
    path_list = []
    for item in unreal.EditorUtilityLibrary.get_selected_assets():
        path_list.append(unreal.EditorUtilityLibrary.get_path_name(item).split(".")[0])
    return path_list


def delete_asset(path: str):
    """删除指定资产

    Args:
        path (str): _description_
    """
    unreal.EditorAssetLibrary.delete_asset(path)
    print(f'删除{path.split("/")[-1]}成功')


def move_assets_with_dialog(assets_path: list[str], target_path):
    """批量移动资产

    Args:
        assets_path (list[str]): 路径
        target_path (_type_): 目标路径
    """
    target_path = process_path_str(target_path)
    if not does_dir_exist(target_path):
        create_dir(target_path)
    with unreal.ScopedSlowTask(len(assets_path), "正在移动资产...") as slow_task:
        slow_task.make_dialog(True)
        for x in range(len(assets_path)):
            if slow_task.should_cancel():
                break
            slow_task.enter_progress_frame(1, f"正在移动资产...\t{x}/{len(assets_path)}")
            move_asset(
                assets_path[x - 1],
                target_path + "/" + assets_path[x - 1].split("/")[-1],
            )
        unreal.EditorAssetLibrary.save_directory(target_path)


def process_assets_name_str(assets_name: Any):
    """处理输入的资产名字，转化为列表

    Args:
        assets_name (Any): _description_

    Returns:
        _type_: _description_
    """
    if type(assets_name) == str:
        return assets_name.split(",")
    elif type(assets_name) == list:
        return assets_name
    else:
        print("无法识别")
        return []


# 醋


def move_selected_assets(target_path: str):
    """移动选定的资产到指定目录

    Args:
        target_path (str, optional):目标路径
    """
    target_path = process_path_str(target_path)
    asset_list = get_selected_assets()
    move_assets_with_dialog(asset_list, target_path)


def move_assents_in_current_dir(assets: Any, target_path: str):
    """移动当前资源浏览器的指定资产至指定路径

    Args:
        assets (Any): 资产名，可以是['a','b'],也可以是'a,b,c'
        target_path (str): 目标路径
    """
    assets_name = process_assets_name_str(assets)
    path = unreal.EditorUtilityLibrary.get_current_content_browser_path()
    assets_path = [f"{path}/{name}" for name in assets_name]
    move_assets_with_dialog(assets_path, target_path)


def move_files_by_pre_in_current_dir(pre: Any, target_path: str):
    """移动指定前缀的文件至目标文件夹（当前资源管理器）

    Args:
        pre (str): 前缀
        target_path (str): 目标路径


    """
    pre = process_assets_name_str(pre)
    items = unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path(
        unreal.EditorUtilityLibrary.get_current_content_browser_path()
    )
    assets_list = []
    for item in items:
        asset_name = item.get_full_name().split(" ", 1)[-1].split("/")[-1].split(".")[0]
        for pr in pre:
            if asset_name.startswith(pr):
                assets_list.append(
                    f"{unreal.EditorUtilityLibrary.get_current_content_browser_path()}/{asset_name}"
                )
                break
    print(assets_list)
    move_assets_with_dialog(assets_list, target_path)


def move_files_by_suf_in_current_dir(suf: str, source_path: str, target_path: str):
    """移动指定后缀的文件至目标文件夹

    Args:
        suf (str): 后缀
        target_path (str): 目标路径

    """
    suf = process_assets_name_str(suf)
    items = unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path(
        unreal.EditorUtilityLibrary.get_current_content_browser_path()
    )
    assets_list = []
    for item in items:
        asset_name = item.get_full_name().split(" ", 1)[-1].split("/")[-1].split(".")[0]
        for pr in suf:
            if asset_name.endswith(pr):
                assets_list.append(
                    f"{unreal.EditorUtilityLibrary.get_current_content_browser_path()}/{asset_name}"
                )
                break
    print(assets_list)
    move_assets_with_dialog(assets_list, target_path)
