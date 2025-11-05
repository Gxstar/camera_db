#!/usr/bin/env python3
"""
超级用户创建脚本 - 类似Django的createsuperuser命令
支持交互式创建管理员用户和创建测试数据
"""

import sys
import getpass
from sqlmodel import Session, select
from database.engine import engine
from model.user import User, UserRole
import bcrypt

def hash_password(password: str) -> str:
    """使用bcrypt哈希密码"""
    # bcrypt限制密码不能超过72字节，需要截断
    if len(password.encode('utf-8')) > 72:
        # 截断到72字节
        password = password.encode('utf-8')[:72].decode('utf-8', 'ignore')
        print("⚠️  密码过长，已自动截断到72字节")
    
    # 直接使用bcrypt库进行哈希
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_superuser():
    """交互式创建超级管理员用户"""
    print("\n🔧 创建超级管理员用户")
    print("=" * 50)
    
    username = input("用户名 (默认: admin): ").strip() or "admin"
    email = input("邮箱 (可选): ").strip() or None
    
    with Session(engine) as session:
        # 检查是否已存在用户
        existing_user = session.exec(select(User).where(User.username == username)).first()
        
        if existing_user:
            print(f"❌ 用户 '{username}' 已存在")
            return False
        
        # 密码输入和验证
        while True:
            password = getpass.getpass("密码: ")
            confirm_password = getpass.getpass("确认密码: ")
            
            if password != confirm_password:
                print("❌ 两次输入的密码不一致，请重新输入")
                continue
                
            if len(password) < 6:
                print("❌ 密码长度至少6位，请重新输入")
                continue
            
            # 检查密码是否超过bcrypt限制
            if len(password.encode('utf-8')) > 72:
                print("⚠️  密码过长（超过72字节），建议使用较短的密码")
                print("💡 系统会自动截断，但建议重新输入较短的密码")
                continue_choice = input("是否继续使用当前密码？(y/N): ").strip().lower()
                if continue_choice not in ['y', 'yes']:
                    continue
                
            break
        
        # 创建管理员用户
        admin_user = User(
            username=username,
            email=email,
            hash_password=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        session.add(admin_user)
        session.commit()
        
        print(f"\n✅ 超级管理员用户创建成功！")
        print(f"   用户名: {username}")
        if email:
            print(f"   邮箱: {email}")
        print(f"   角色: {UserRole.ADMIN}")
        print("\n💡 请妥善保管密码，首次登录后建议修改密码")
        return True

def create_test_data():
    """创建测试数据"""
    print("\n🔧 创建测试数据")
    print("=" * 50)
    
    with Session(engine) as session:
        # 创建测试管理员（如果不存在）
        existing_admin = session.exec(select(User).where(User.username == "admin")).first()
        if not existing_admin:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hash_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            session.add(admin_user)
            print("✅ 创建测试管理员: admin / admin123")
        else:
            print("ℹ️  测试管理员已存在")
        
        # 创建测试普通用户（如果不存在）
        existing_user = session.exec(select(User).where(User.username == "testuser")).first()
        if not existing_user:
            test_user = User(
                username="testuser",
                email="user@example.com",
                hash_password=hash_password("user123"),
                role=UserRole.USER,
                is_active=True
            )
            session.add(test_user)
            print("✅ 创建测试用户: testuser / user123")
        else:
            print("ℹ️  测试用户已存在")
        
        session.commit()
    
    print("\n✅ 测试数据创建完成！")
    print("\n测试账号信息：")
    print("- 管理员: admin / admin123")
    print("- 普通用户: testuser / user123")
    return True

def show_help():
    """显示帮助信息"""
    print("""
📋 超级用户管理脚本 - 使用方法

命令:
    python create_superuser.py          交互式创建超级管理员
    python create_superuser.py testdata 创建测试数据
    python create_superuser.py help     显示此帮助信息

示例:
    # 交互式创建管理员
    python create_superuser.py
    
    # 创建测试数据（开发环境）
    python create_superuser.py testdata
""")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "testdata":
            try:
                create_test_data()
            except Exception as e:
                print(f"❌ 创建测试数据失败: {e}")
                sys.exit(1)
        elif command in ["help", "--help", "-h"]:
            show_help()
        else:
            print(f"❌ 未知命令: {command}")
            show_help()
            sys.exit(1)
    else:
        # 默认行为：交互式创建超级管理员
        try:
            create_superuser()
        except Exception as e:
            print(f"❌ 创建超级管理员失败: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()