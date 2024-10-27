#!/usr/bin/env python3

import importlib.metadata
import re
import os

# 解析包的版本规范
def parse_package_spec(spec):
    """
    解析包名和版本规范。
    返回 (name, operator, version)。
    """
    match = re.match(r'^([^=<>!~]+)\s*([=<>!~]+)\s*(.+)$', spec)
    if match:
        name, op, version = match.groups()
        return name.strip(), op.strip(), version.strip()
    else:
        return spec.strip(), None, None

# 获取已安装包的版本
def get_installed_versions(packages):
    installed_versions = {}
    for pkg in packages:
        name, _, _ = parse_package_spec(pkg)
        try:
            installed_version = importlib.metadata.version(name)
            installed_versions[name] = installed_version
        except importlib.metadata.PackageNotFoundError:
            print(f"包 {name} 未安装。")
            continue
    return installed_versions

# 读取现有的 requirements.txt
def read_requirements(file_path='requirements.txt'):
    req_versions = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                name, op, version_spec = parse_package_spec(line)
                if op and version_spec:
                    req_versions[name] = f"{op}{version_spec}"
                else:
                    req_versions[name] = None  # 未指定版本
    return req_versions

# 合并包信息
def merge_requirements(installed_versions, req_versions):
    merged_requirements = []
    conflict_detected = False
    processed_packages = set()

    for name, installed_version in installed_versions.items():
        if name in req_versions:
            req_version_spec = req_versions[name]
            if req_version_spec:
                # 检查版本是否匹配
                version_match = False
                # 支持多种版本操作符
                ops = ['==', '>=', '<=', '>', '<', '!=', '~=']
                for op in ops:
                    if req_version_spec.startswith(op):
                        req_op = op
                        req_ver = req_version_spec[len(op):]
                        break
                else:
                    req_op = None
                    req_ver = None

                if req_op == '==':
                    if req_ver == installed_version:
                        merged_requirements.append(f"{name}=={installed_version}")
                    else:
                        # 版本冲突
                        merged_requirements.append(f"<<<<<<< HEAD")
                        merged_requirements.append(f"{name}{req_version_spec}")
                        merged_requirements.append(f"=======")
                        merged_requirements.append(f"{name}=={installed_version}")
                        merged_requirements.append(f">>>>>>> Merged version")
                        conflict_detected = True
                else:
                    # 如果 requirements.txt 中有版本规范但不是 '=='
                    # 可以根据需要调整此逻辑
                    # 这里假设只在 '==' 时进行严格匹配
                    # 其他情况下认为没有冲突
                    merged_requirements.append(f"{name}{req_version_spec}")
            else:
                # requirements.txt 未指定版本，直接覆盖为已安装版本
                merged_requirements.append(f"{name}=={installed_version}")
            processed_packages.add(name)
        else:
            # 包不在 requirements.txt 中，添加已安装版本
            merged_requirements.append(f"{name}=={installed_version}")
            processed_packages.add(name)

    # 添加 requirements.txt 中未处理的包
    for name, version_spec in req_versions.items():
        if name not in processed_packages:
            if version_spec:
                merged_requirements.append(f"{name}{version_spec}")
            else:
                merged_requirements.append(f"{name}")

    return merged_requirements, conflict_detected

def main():
    # 读取现有的 requirements.txt 获取包列表
    req_versions = read_requirements('requirements.txt')
    packages = list(req_versions.keys())

    # 获取已安装包的版本
    installed_versions = get_installed_versions(packages)

    # 合并包信息
    merged_requirements, conflict_detected = merge_requirements(installed_versions, req_versions)

    # 将合并结果写回 requirements.txt
    with open('requirements.txt', 'w') as f:
        for line in merged_requirements:
            f.write(line + '\n')

    if conflict_detected:
        print("requirements.txt 已更新，存在版本冲突。请手动解决冲突标记。")
    else:
        print("requirements.txt 已更新，无版本冲突。")

if __name__ == "__main__":
    main()