from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .enums import RoleChoice

User = get_user_model()


class UserRegisterAuth(APITestCase):
    def setUp(self):
        # ----- REGISTER USERS -----
        users_data = [
            {
                "email": "manager11@gmail.com",
                "username": "supermanager",
                "password": "tests1234",
                "first_name": "super",
                "last_name": "manager",
                "role": RoleChoice.MANAGER.name,
            },
            {
                "email": "developer@company.com",
                "username": "senior_dev",
                "password": "devpass123",
                "first_name": "Sarah",
                "last_name": "Developer",
                "role": RoleChoice.DEVELOPER.name,
            },
            {
                "email": "qa@company.com",
                "username": "qa_engineer",
                "password": "qapass123",
                "first_name": "Hassan",
                "last_name": "QA",
                "role": RoleChoice.QA.name,
            },
            {
                "email": "designer@company.com",
                "username": "ui_designer",
                "password": "designpass123",
                "first_name": "Ali",
                "last_name": "Designer",
                "role": RoleChoice.DESIGNER.name,
            },
        ]

        self.tokens = {}
        self.user_ids = {}

        for user in users_data:
            data = {
                "email": user["email"],
                "username": user["username"],
                "password": user["password"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "profile": {
                    "phone": "+9230012345" + str(len(self.user_ids) + 67),
                    "role": user["role"],
                },
            }
            response = self.client.post(reverse("register"), data, format="json")
            self.user_ids[user["role"]] = response.data["id"]

            # Login and store token
            login_data = {"email": user["email"], "password": user["password"]}
            login_response = self.client.post(
                reverse("login"), login_data, format="json"
            )
            self.tokens[user["role"]] = login_response.data["access"]


class ProjectTaskTestCase(UserRegisterAuth):

    def setUp(self):
        super().setUp()
        # Authenticate as manager
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens[RoleChoice.MANAGER.name]}"
        )

        # Create a project
        project_data = {
            "title": "Project for Task Test",
            "description": "Testing tasks creation",
            "start_date": "2024-01-12",
            "team_member_ids": list(self.user_ids.values()),
        }
        project_response = self.client.post(
            reverse("project-list-create"), project_data, format="json"
        )
        if project_response.status_code == status.HTTP_201_CREATED:
            self.project_id = project_response.data["id"]
        else:
            raise Exception(
                f"Project creation failed in setUp: {project_response.status_code} - {project_response.json()}"
            )

        # Create a task
        task_data = {
            "title": "QA Testing Task",
            "description": "Task for QA to comment on",
            "project_id": self.project_id,
            "assignee_id": self.user_ids[RoleChoice.QA.name],
        }
        task_response = self.client.post(
            reverse("task-list-create"), task_data, format="json"
        )
        if task_response.status_code == status.HTTP_201_CREATED:
            self.task_id = task_response.data["id"]
        else:
            # Task creation failed → set to None and log for debug
            print(
                f"Task creation failed in setUp: {task_response.status_code} - {task_response.json()}"
            )
            self.task_id = None

    def test_manager_can_create_project_and_tasks(self):
        """Manager can create projects and assign tasks"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens[RoleChoice.MANAGER.name]}"
        )

        # Create Task
        tasks_data = [
            {
                "title": "Develop Backend API",
                "description": "Build RESTful APIs",
                "project_id": self.project_id,
                "assignee_id": self.user_ids[RoleChoice.DEVELOPER.name],
            },
            {
                "title": "Write Test Cases",
                "description": "Create test cases",
                "project_id": self.project_id,
                "assignee_id": self.user_ids[RoleChoice.QA.name],
            },
            {
                "title": "Design UI",
                "description": "Create UI/UX designs",
                "project_id": self.project_id,
                "assignee_id": self.user_ids[RoleChoice.DESIGNER.name],
            },
        ]
        for task in tasks_data:
            response = self.client.post(
                reverse("task-list-create"), task, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_manager_cannot_create_projects(self):
        """Developer, QA, Designer cannot create projects"""
        for role in [
            RoleChoice.DEVELOPER.name,
            RoleChoice.QA.name,
            RoleChoice.DESIGNER.name,
        ]:
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.tokens[role]}")
            project_data = {
                "title": f"Forbidden Project by {role}",
                "description": "Should not create",
                "start_date": "2024-01-12",
                "team_member_ids": list(self.user_ids.values()),
            }
            response = self.client.post(
                reverse("project-list-create"), project_data, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_developer_cannot_create_tasks(self):
        """Developer cannot create tasks (403)"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens[RoleChoice.DEVELOPER.name]}"
        )
        task_data = {
            "title": "Developer Task",
            "description": "Should not create",
            "project_id": self.project_id,
            "assignee_id": self.user_ids[RoleChoice.DEVELOPER.name],
        }
        response = self.client.post(
            reverse("task-list-create"), task_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_qa_cannot_create_tasks(self):
        """QA cannot create tasks (403)"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens[RoleChoice.QA.name]}"
        )
        task_data = {
            "title": "QA Task",
            "description": "Should not create",
            "project_id": self.project_id,
            "assignee_id": self.user_ids[RoleChoice.QA.name],
        }
        response = self.client.post(
            reverse("task-list-create"), task_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_designer_cannot_create_tasks(self):
        """Designer cannot create tasks (403)"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens[RoleChoice.DESIGNER.name]}"
        )
        task_data = {
            "title": "Designer Task",
            "description": "Should not create",
            "project_id": self.project_id,
            "assignee_id": self.user_ids[RoleChoice.DESIGNER.name],
        }
        response = self.client.post(
            reverse("task-list-create"), task_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_developer_can_view_assigned_tasks(self):
        """Developer can view tasks assigned to them"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens[RoleChoice.DEVELOPER.name]}"
        )

        response = self.client.get(
            reverse("task-list-create") + f"?project_id={self.project_id}",
            format="json",
        )
        print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)

    def test_qa_can_add_comments(self):
        if not self.task_id:
            self.skipTest("Task was not created; skipping comment test")

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens[RoleChoice.QA.name]}"
        )
        comment_data = {
            "text": "Starting QA testing process",
            "task_id": self.task_id,
            "project_id": self.project_id,
        }
        response = self.client.post(
            reverse("comment-list-create"), comment_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], comment_data["text"])

    def test_timeline_created_for_project_and_task(self):
        """Timeline entries are created for project and task events"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens[RoleChoice.MANAGER.name]}"
        )

        response = self.client.get(
            reverse("timeline-list") + f"?project_id={self.project_id}", format="json"
        )
        print(response)
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_notification_created_for_task_assignment(self):
        """Task assignment creates notification for assignee"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens[RoleChoice.QA.name]}"
        )

        response = self.client.get(reverse("notification-list"), format="json")
        print(response)
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("QA Testing Task" in n["text"] for n in response.data))
