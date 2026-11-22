# Quickstart: Testing SSO Authentication & External User Directory

Follow these steps to verify SSO-only authentication and external user directory retrieval.

---

## 1. Prerequisites

- FastAPI backend running (or test ASGI client).
- Valid SSO Access Token:
  ```bash
  export SSO_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3OTU4NDMwNjEsInR5cGUiOiJhY2Nlc3MiLCJzdWIiOiIxIiwibmFtZSI6Ikh1XHUxZWYzbmggUGhcdTAxYjBcdTFlZGJjIE5ndXlcdTAwZWFuIiwiZW1haWwiOiJodXluaHBodW9jbmd1eWVuLmRldkBnbWFpbC5jb20iLCJyb2xlcyI6WyJhZG1pbiIsIlRyYWluZXIiXSwiYXZhdGFyIjoiaHR0cHM6Ly9taW5pby5kdXRhaS5zaXRlL2R1dC1haS1tYW5hZ2VyLXByb2QvYXZhdGFycy8xXzIwMjYwODIxXzE3MTg0My5qcGciLCJwZXJtaXNzaW9ucyI6WyJhY2NvdW50OmNyZWF0ZSIsImFjY291bnQ6ZGVsZXRlIiwiYWNjb3VudDpyZWFkIiwiYWNjb3VudDp1cGRhdGUiLCJiaWxsaW5nOmNyZWF0ZSIsImJpbGxpbmc6ZGVsZXRlIiwiYmlsbGluZzpteV9pbnZvaWNlcyIsImJpbGxpbmc6cmVhZCIsImJpbGxpbmc6dXBkYXRlIiwiYm9udXNfcG9pbnQ6Y3JlYXRlIiwiYm9udXNfcG9pbnQ6ZGVsZXRlIiwiYm9udXNfcG9pbnQ6cmVhZCIsImJvbnVzX3BvaW50OnVwZGF0ZSIsImV4cGVuc2U6Y3JlYXRlIiwiZXhwZW5zZTpkZWxldGUiLCJleHBlbnNlOnJlYWQiLCJleHBlbnNlOnVwZGF0ZSIsImhvbWV3b3JrOmNyZWF0ZSIsImhvbWV3b3JrOmRlbGV0ZSIsImhvbWV3b3JrOnJlYWQiLCJob21ld29yazp1cGRhdGUiLCJob21ld29ya19zdWJtaXNzaW9uOmNyZWF0ZSIsImhvbWV3b3JrX3N1Ym1pc3Npb246ZGVsZXRlIiwiaG9tZXdvcmtfc3VibWlzc2lvbjpyZWFkIiwiaG9tZXdvcmtfc3VibWlzc2lvbjp1cGRhdGUiLCJtZWV0aW5nOmNoZWNrX2luIiwibWVldGluZzpjcmVhdGUiLCJtZWV0aW5nOmRlbGV0ZSIsIm1lZXRpbmc6cmVhZCIsIm1lZXRpbmc6dXBkYXRlIiwicGVybWlzc2lvbjpjcmVhdGUiLCJwZXJtaXNzaW9uOmRlbGV0ZSIsInBlcm1pc3Npb246cmVhZCIsInBlcm1pc3Npb246dXBkYXRlIiwicGVybWlzc2lvbl9yZXF1ZXN0OmNyZWF0ZSIsInBlcm1pc3Npb25fcmVxdWVzdDpkZWxldGUiLCJwZXJtaXNzaW9uX3JlcXVlc3Q6cmVhZCIsInBlcm1pc3Npb25fcmVxdWVzdDp1cGRhdGUiLCJyb2xlOmNyZWF0ZSIsInJvbGU6ZGVsZXRlIiwicm9sZTpyZWFkIiwicm9sZTp1cGRhdGUiLCJ0ZWFtOmNyZWF0ZSIsInRlYW06ZGVsZXRlIiwidGVhbTpyZWFkIiwidGVhbTp1cGRhdGUiLCJ0ZWFtX21lbWJlcjpjcmVhdGUiLCJ0ZWFtX21lbWJlcjpkZWxldGUiLCJ0ZWFtX21lbWJlcjpyZWFkIiwidGVhbV9tZW1iZXI6dXBkYXRlIiwidXNlcjpjcmVhdGUiLCJ1c2VyOmRlbGV0ZSIsInVzZXI6cmVhZCIsInVzZXI6dXBkYXRlIiwidmlvbGF0aW9uOmNyZWF0ZSIsInZpb2xhdGlvbjpkZWxldGUiLCJ2aW9sYXRpb246cmVhZCIsInZpb2xhdGlvbjp1cGRhdGUiXX0.k7VfTQ_kZ_u2_VcTCimxKJbiGHl9Qd6kDpStJerKtkk"
  ```

---

## 2. Test Verification Steps

### Step 1: Query Current Authenticated User (`/me`)
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $SSO_TOKEN"
```
**Expected Outcome**: Returns `id: 1` as integer and profile details without querying local user database.

---

### Step 2: List User Options (`/users/options`)
```bash
curl -X GET "http://localhost:8000/api/v1/users/options" \
  -H "Authorization: Bearer $SSO_TOKEN"
```
**Expected Outcome**: Returns array of user objects where each `id` is an integer.

---

### Step 3: Query User Detail by Integer ID (`/users/1`)
```bash
curl -X GET "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer $SSO_TOKEN"
```
**Expected Outcome**: Returns full user profile for ID 1.

---

### Step 4: Verify Non-Integer ID Rejection (`/users/abc`)
```bash
curl -X GET "http://localhost:8000/api/v1/users/abc" \
  -H "Authorization: Bearer $SSO_TOKEN"
```
**Expected Outcome**: HTTP 422 Unprocessable Entity (strictly rejected by integer path constraint).
