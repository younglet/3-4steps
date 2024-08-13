from pathlib import Path

# 获取当前工作目录
current_path = Path.cwd()

# 打印当前工作目录
print(f"当前工作目录: {current_path}")

# 遍历当前目录下的所有文件和子目录
for child in current_path.iterdir():
    # 输出每个子项的名字
    print(f"子项名称: {child.name}")
    
    # 检查子项是否为文件
    if child.is_file():
        print(f"  - 是文件: {child}")
        
        # 获取文件扩展名
        print(f"    文件后缀: {child.suffix}")
        
    # 检查子项是否为目录
    elif child.is_dir():
        print(f"  - 是目录: {child}")

# 检查当前工作目录是否存在
if current_path.exists():
    print(f"当前目录存在: {current_path.exists()}")

# 获取当前目录的父目录
parent_directory = current_path.parent
print(f"父目录: {parent_directory}")

# 创建一个新的子目录
new_subdirectory = current_path / "new_subdirectory"
new_subdirectory.mkdir(exist_ok=True)
print(f"创建新子目录: {new_subdirectory}")

# 删除新创建的子目录
new_subdirectory.rmdir()
print(f"删除新子目录: {new_subdirectory}")