from sqlalchemy import text
from database import SessionLocal, engine
from models import User, Hospital, Patient

def view_operation():
    """Example of VIEW (Read) operation"""
    db = SessionLocal()
    try:
        # Get all users
        users = db.query(User).all()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f" - {user.name} ({user.email})")
        
        # Get a specific hospital
        hospital = db.query(Hospital).filter(Hospital.email == "hospital@shms.com").first()
        if hospital:
            print(f"Found Hospital: {hospital.name}")
    finally:
        db.close()

def insert_operation():
    """Example of INSERT operation"""
    db = SessionLocal()
    try:
        new_user = User(
            name="Demo User",
            email="demo@example.com",
            password="password123",
            role="user"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"Inserted User with ID: {new_user.id}")
    except Exception as e:
        db.rollback()
        print(f"Insert failed: {e}")
    finally:
        db.close()

def update_operation():
    """Example of UPDATE operation"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@example.com").first()
        if user:
            user.name = "Updated Demo User"
            db.commit()
            print("User updated successfully.")
    except Exception as e:
        db.rollback()
        print(f"Update failed: {e}")
    finally:
        db.close()

def delete_operation():
    """Example of DELETE operation"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@example.com").first()
        if user:
            db.delete(user)
            db.commit()
            print("User deleted successfully.")
    finally:
        db.close()

def alter_operation():
    """Example of ALTER operation (Using raw SQL)"""
    # Note: SQLAlchemy models handle the schema, but sometimes you need raw SQL for migrations
    with engine.connect() as conn:
        try:
            # Example: Adding a 'phone' column to User table if it didn't exist
            # conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20)"))
            # conn.commit()
            print("Alter table command example (commented out in code for safety)")
            pass
        except Exception as e:
            print(f"Alter failed: {e}")

if __name__ == "__main__":
    print("--- Database Operations Demo ---")
    print("\n1. Running View Operation:")
    view_operation()
    
    # These are commented out to prevent affecting your project data directly
    # print("\n2. Running Insert Operation:")
    # insert_operation()
    
    # print("\n3. Running Update Operation:")
    # update_operation()
    
    # print("\n4. Running Delete Operation:")
    # delete_operation()
    
    # print("\n5. Running Alter Operation:")
    # alter_operation()
