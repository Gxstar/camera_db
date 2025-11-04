#!/usr/bin/env python3
"""
测试用户数据创建脚本
用于创建管理员和普通用户，用于权限验证测试
"""

import sys
from sqlmodel import Session, select
from database.engine import engine
from model.user import User, UserRole
from model.brand import Brand
from model.camera import Camera

def create_test_data():
    """创建测试数据"""
    with Session(engine) as session:
        # 检查是否已存在测试用户
        existing_admin = session.exec(select(User).where(User.username == "admin")).first()
        existing_user = session.exec(select(User).where(User.username == "testuser")).first()
        
        if existing_admin:
            print("管理员用户已存在，跳过创建")
        else:
            # 创建管理员用户
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="系统管理员",
                role=UserRole.ADMIN,
                is_active=True
            )
            admin_user.set_password("admin123")
            session.add(admin_user)
            print("创建管理员用户: admin / admin123")
        
        if existing_user:
            print("普通用户已存在，跳过创建")
        else:
            # 创建普通用户
            test_user = User(
                username="testuser",
                email="user@example.com",
                full_name="测试用户",
                role=UserRole.USER,
                is_active=True
            )
            test_user.set_password("user123")
            session.add(test_user)
            print("创建普通用户: testuser / user123")
        
        session.commit()
        print("测试用户数据创建完成！")

def main():
    """主函数"""
    try:
        create_test_data()
        print("\n测试用户信息：")
        print("- 管理员: admin / admin123 (ADMIN角色)")
        print("- 普通用户: testuser / user123 (USER角色)")
        print("\n使用这些账号测试权限验证功能。")
    except Exception as e:
        print(f"创建测试数据时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()