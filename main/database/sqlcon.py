from sqlalchemy import create_engine, Column, Integer, String, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


Base = declarative_base()
engine = create_engine("sqlite:///milvus_demo.db", echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = SessionLocal()

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    info = Column(String)
    permission = Column(String, unique=False)
    email = Column(String, unique=True, index=True)
    # apikey = Column(String, unique=True)


def init_db():
    # Create an inspector
    inspector = inspect(engine)

    # Check if the 'users' table exists
    if not inspector.has_table('users'):
        # Create all tables in the engine
        Base.metadata.create_all(engine)
        print("Database initialized. Tables created.")
    else:
        print("Database already initialized. Tables exist.")

init_db()

# new_user = UserDB(username='John Doe', info="", email= "example@example.com")
# session.add(new_user)
# session.commit()


# print(session.query(UserDB).all()[0].username)