from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Setup a SEPARATE Test Database so we don't affect the main project
TEST_DB_URL = "sqlite:///./test_shms_demo.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define a simple model for the demo
class DemoUser(Base):
    __tablename__ = "demo_users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)

def run_full_demo():
    # CREATE TABLES in the test database
    print("--- Creating Tables in TEST database ---")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # --- INSERT OPERATION ---
        print("\n1. [INSERT] Adding a new user...")
        user1 = DemoUser(name="Test User", email="test@demo.com")
        db.add(user1)
        db.commit()
        db.refresh(user1)
        print(f"   Success: Added {user1.name} with ID {user1.id}")

        # --- VIEW OPERATION ---
        print("\n2. [VIEW] Reading all users...")
        users = db.query(DemoUser).all()
        for u in users:
            print(f"   - ID: {u.id}, Name: {u.name}, Email: {u.email}")

        # --- UPDATE OPERATION ---
        print("\n3. [UPDATE] Updating user's name...")
        user_to_update = db.query(DemoUser).filter(DemoUser.email == "test@demo.com").first()
        if user_to_update:
            user_to_update.name = "Updated Test User"
            db.commit()
            print(f"   Success: Name changed to {user_to_update.name}")

        # --- ALTER OPERATION ---
        print("\n4. [ALTER] Adding a 'phone' column via raw SQL...")
        with engine.connect() as conn:
            # Check if column exists (simple check for demo)
            try:
                conn.execute(text("ALTER TABLE demo_users ADD COLUMN phone TEXT"))
                conn.commit()
                print("   Success: Column 'phone' added to table.")
            except Exception:
                print("   Note: Column 'phone' might already exist.")

        # --- DELETE OPERATION ---
        print("\n5. [DELETE] Removing the user...")
        user_to_delete = db.query(DemoUser).filter(DemoUser.email == "test@demo.com").first()
        if user_to_delete:
            db.delete(user_to_delete)
            db.commit()
            print("   Success: User removed from database.")

        # FINAL VIEW
        print("\n6. [VIEW] Final check of users:")
        remaining = db.query(DemoUser).count()
        print(f"   Remaining users: {remaining}")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_full_demo()
    print("\nDemo complete! This did NOT touch your 'shms.db' file.")
