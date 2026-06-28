# tech-spec.md

## Stack
- **Language**: TypeScript
- **Framework**: Node.js with Express for the backend; React for the frontend
- **Runtime**: Docker containers for local development and deployment

## Hosting
- **Free Tier**: 
  - Vercel for frontend hosting
  - DigitalOcean App Platform for backend hosting
- **Specific Platforms**: 
  - AWS for scalable deployment options
  - Local deployment via Docker for users preferring local-first solutions

## Data Model
### Collections
1. **Users**
   - `user_id`: UUID (Primary Key)
   - `username`: String (Unique)
   - `email`: String (Unique)
   - `password_hash`: String
   - `created_at`: Timestamp
   - `updated_at`: Timestamp

2. **Projects**
   - `project_id`: UUID (Primary Key)
   - `user_id`: UUID (Foreign Key)
   - `project_name`: String
   - `created_at`: Timestamp
   - `updated_at`: Timestamp

3. **Code Snippets**
   - `snippet_id`: UUID (Primary Key)
   - `project_id`: UUID (Foreign Key)
   - `code`: Text
   - `language`: String
   - `created_at`: Timestamp
   - `updated_at`: Timestamp

4. **Search Queries**
   - `query_id`: UUID (Primary Key)
   - `user_id`: UUID (Foreign Key)
   - `query_text`: String
   - `timestamp`: Timestamp

## API Surface
1. **User Registration**
   - **Method**: POST
   - **Path**: `/api/users/register`
   - **Purpose**: Register a new user

2. **User Login**
   - **Method**: POST
   - **Path**: `/api/users/login`
   - **Purpose**: Authenticate user and return access token

3. **Create Project**
   - **Method**: POST
   - **Path**: `/api/projects`
   - **Purpose**: Create a new project for the authenticated user

4. **Add Code Snippet**
   - **Method**: POST
   - **Path**: `/api/snippets`
   - **Purpose**: Add a new code snippet to a project

5. **Search Code Snippets**
   - **Method**: GET
   - **Path**: `/api/snippets/search`
   - **Purpose**: Search for code snippets based on query parameters

6. **Get User Projects**
   - **Method**: GET
   - **Path**: `/api/projects`
   - **Purpose**: Retrieve all projects for the authenticated user

7. **Get Code Snippet**
   - **Method**: GET
   - **Path**: `/api/snippets/:snippet_id`
   - **Purpose**: Retrieve a specific code snippet by ID

8. **Delete Code Snippet**
   - **Method**: DELETE
   - **Path**: `/api/snippets/:snippet_id`
   - **Purpose**: Delete a specific code snippet by ID

## Security Model
- **Authentication**: JWT (JSON Web Tokens) for user sessions
- **Secrets Management**: Use AWS Secrets Manager for storing sensitive information like database credentials
- **IAM**: Role-based access control (RBAC) to manage permissions for different user roles (e.g., admin, user)

## Observability
- **Logs**: Use Winston for logging application events and errors
- **Metrics**: Integrate Prometheus for collecting application metrics
- **Traces**: Use OpenTelemetry for distributed tracing to monitor performance and troubleshoot issues

## Build/CI
- **Build Tool**: Webpack for bundling frontend assets
- **CI/CD Pipeline**: GitHub Actions for continuous integration and deployment
  - **Steps**:
    1. Linting and testing on every push
    2. Build Docker images for deployment
    3. Deploy to staging environment on merge to main branch
    4. Manual approval for production deployment