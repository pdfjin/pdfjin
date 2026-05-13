from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

h = "$2b$12$t7Iz1arH8JOdpdzzMh7iQOWwnv3/EN/baHwvrY9WNxQTaHFWK4s3O"
p = "pdfjin-admin-2026"

print(f"Password match: {pwd_context.verify(p, h)}")
