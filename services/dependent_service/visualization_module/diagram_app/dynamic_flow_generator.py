import ast
from pathlib import Path


class DynamicFlowGenerator:
    """Generate sequence and activity diagrams from actual view functions"""

    def __init__(self):
        self.services_path = Path("services")
        self.sequence_output = Path("docs/diagrams/plantuml/sequences")
        self.activity_output = Path("docs/diagrams/plantuml/activities")
        self.sequence_output.mkdir(parents=True, exist_ok=True)
        self.activity_output.mkdir(parents=True, exist_ok=True)

    def _find_view_files(self):
        """Find all views.py files in the project"""
        view_files = []
        for views_file in self.services_path.rglob("views.py"):
            if "__pycache__" not in str(views_file):
                view_files.append(views_file)
        return view_files

    def _extract_view_info(self, view_file):
        """Extract view classes and methods from a views file"""
        try:
            with open(view_file, "r") as f:
                tree = ast.parse(f.read())

            views = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if not item.name.startswith("_"):
                                methods.append(item.name)
                    if methods:
                        views.append(
                            {"class": node.name, "methods": methods, "file": view_file}
                        )
            return views
        except Exception as e:
            print(f"error {str(e)}")

            return []

    def _generate_sequence_for_view(self, view_info):
        """Generate sequence diagram for a view"""
        class_name = view_info["class"]
        module_name = view_info["file"].parent.parent.name

        content = [
            "@startuml",
            "autonumber",
            "actor User",
            'participant "API" as API',
            f'participant "{class_name}" as View',
            'participant "Service" as Service',
            'database "Database" as DB',
            "",
        ]

        for method in view_info["methods"][:3]:  # Limit to first 3 methods
            http_method = "GET" if method in ["get", "list", "retrieve"] else "POST"
            content.extend(
                [
                    f"User -> API: {http_method} /api/{module_name}/",
                    f"API -> View: {method}()",
                    "View -> Service: process()",
                    "Service -> DB: query()",
                    "DB --> Service: data",
                    "Service --> View: result",
                    "View --> API: response",
                    "API --> User: 200 OK",
                    "",
                ]
            )

        content.append("@enduml")

        filename = f"sequence_{module_name}_{class_name}.puml"
        (self.sequence_output / filename).write_text("\n".join(content))
        return filename

    def _generate_activity_for_view(self, view_info):
        """Generate activity diagram for a view"""
        class_name = view_info["class"]
        module_name = view_info["file"].parent.parent.name

        content = [
            "@startuml",
            "start",
            ":Receive HTTP Request;",
            "",
        ]

        for method in view_info["methods"][:5]:
            method_title = method.replace("_", " ").title()

            if method in ["get", "list", "retrieve"]:
                content.extend(
                    [
                        f":{method_title};",
                        ":Validate permissions;",
                        "if (Has permission?) then (yes)",
                        "  :Query database;",
                        "  :Serialize data;",
                        "  :Return 200 OK;",
                        "else (no)",
                        "  :Return 403 Forbidden;",
                        "endif",
                        "",
                    ]
                )
            elif method in ["post", "create"]:
                content.extend(
                    [
                        f":{method_title};",
                        ":Validate request data;",
                        "if (Valid data?) then (yes)",
                        "  :Check permissions;",
                        "  if (Has permission?) then (yes)",
                        "    :Save to database;",
                        "    :Return 201 Created;",
                        "  else (no)",
                        "    :Return 403 Forbidden;",
                        "  endif",
                        "else (no)",
                        "  :Return 400 Bad Request;",
                        "endif",
                        "",
                    ]
                )
            elif method in ["put", "patch", "update", "partial_update"]:
                content.extend(
                    [
                        f":{method_title};",
                        ":Validate request data;",
                        "if (Valid data?) then (yes)",
                        "  :Check permissions;",
                        "  if (Has permission?) then (yes)",
                        "    :Update database;",
                        "    :Return 200 OK;",
                        "  else (no)",
                        "    :Return 403 Forbidden;",
                        "  endif",
                        "else (no)",
                        "  :Return 400 Bad Request;",
                        "endif",
                        "",
                    ]
                )
            elif method in ["delete", "destroy"]:
                content.extend(
                    [
                        f":{method_title};",
                        ":Check permissions;",
                        "if (Has permission?) then (yes)",
                        "  :Delete from database;",
                        "  :Return 204 No Content;",
                        "else (no)",
                        "  :Return 403 Forbidden;",
                        "endif",
                        "",
                    ]
                )
            else:
                content.extend(
                    [
                        f":{method_title};",
                        ":Process request;",
                        ":Return response;",
                        "",
                    ]
                )

        content.extend(
            [
                "stop",
                "@enduml",
            ]
        )

        filename = f"activity_{module_name}_{class_name}.puml"
        (self.activity_output / filename).write_text("\n".join(content))
        return filename

    def generate_all_sequences(self):
        """Generate sequence diagrams for all views"""
        view_files = self._find_view_files()
        generated = []

        for view_file in view_files:
            views = self._extract_view_info(view_file)
            for view_info in views[:2]:  # Limit to 2 views per file
                try:
                    filename = self._generate_sequence_for_view(view_info)
                    generated.append(filename)
                except Exception as e:
                    print(f"error {str(e)}")

        return generated

    def generate_all_activities(self):
        """Generate activity diagrams for all views"""
        view_files = self._find_view_files()
        generated = []

        for view_file in view_files:
            views = self._extract_view_info(view_file)
            for view_info in views[:2]:  # Limit to 2 views per file
                try:
                    filename = self._generate_activity_for_view(view_info)
                    generated.append(filename)
                except Exception as e:
                    print(f"error {str(e)}")

        return generated
