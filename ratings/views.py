from django.shortcuts import render
from django.contrib.auth.models import User

from .models import Professor, Module, Rating
from .serializers import ProfessorSerializer, ModuleSerializer, RatingSerializer, RegisterSerializer

from rest_framework import generics
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, AllowAny

# Option 1: List all modules with professors
class ModuleListView(APIView):
    def get(self, request):
        modules = Module.objects.all()
        data = []
        for module in modules:
            professors = module.professors.all()  # ManyToMany relation
            professor_list = [{"id": prof.id, "name": prof.name} for prof in professors]
            data.append({
                "code": module.code,
                "name": module.name,
                "year": module.year,
                "semester": module.semester,
                "professors": professor_list
            })
        return Response(data)
    
# Option 2: List all professors and their ratings
class ProfessorListView(APIView):
    def get(self, request):
        professors = Professor.objects.all()
        data = []
        rating_labels = {
            1: "Unbearable",
            2: "Bad",
            3: "Decent",
            4: "Smart",
            5: "Excellent"
        }

        for prof in professors:
            ratings = prof.ratings.all()  # Reverse relationship
            if ratings.exists():
                avg_rating = round(sum(r.rating for r in ratings) / ratings.count())  # Round to nearest integer
                label = rating_labels.get(avg_rating, "No ratings yet")
                stars = "⭐" * avg_rating
            else:
                avg_rating = "No ratings yet"
                label = avg_rating
                stars = ""

            # Fetch modules the professor is teaching
            modules = prof.modules.all()  # Assuming ManyToMany relationship
            module_list = [{"code": mod.code, "name": mod.name} for mod in modules]

            data.append({
                "id": prof.id,
                "name": prof.name,
                "average_rating": f"{stars} ({label})" if isinstance(avg_rating, int) else avg_rating,
                "modules": module_list
            })

        return Response(data)

# Option 3: View ratings for a specific professor in a module
class ProfessorRatingView(APIView):
    def get(self, request, professor_id, module_code):
        year = request.query_params.get("year")  # Get year from request
        semester = request.query_params.get("semester")  # Get semester from request

        try:
            professor = Professor.objects.get(id=professor_id)
        except Professor.DoesNotExist:
            return Response({"detail": "❌ Professor not found."}, status=404)

        try:
            module = Module.objects.get(code=module_code)
        except Module.DoesNotExist:
            return Response({"detail": "❌ Module not found."}, status=404)

        # Apply filtering for year and semester
        filters = {"professor": professor, "module": module}
        if year:
            filters["module__year"] = year
        if semester:
            filters["module__semester"] = semester

        ratings = Rating.objects.filter(**filters)

        if not ratings.exists():
            return Response({
                "professor_name": professor.name,
                "professor_id": professor.id,
                "module_name": module.name,
                "module_code": module.code,
                "average_rating": "No ratings yet"
            })

        # Calculate average rating
        avg_rating = sum(r.rating for r in ratings) / ratings.count()
        avg_rating = round(avg_rating)  # Round to nearest integer

        return Response({
            "professor_name": professor.name,
            "professor_id": professor.id,
            "module_name": module.name,
            "module_code": module.code,
            "year": year,
            "semester": semester,
            "average_rating": avg_rating  # Send numeric value
        })

# Option 4: Allow students to rate a professor
class RateProfessorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        professor_id = data.get("professor")
        module_code = data.get("module")
        year = data.get("year")
        semester = data.get("semester")
        rating = data.get("rating")

        if not all([professor_id, module_code, year, semester, rating]):
            return Response({"detail": "All fields are required."}, status=400)

        if not (1 <= int(rating) <= 5):
            return Response({"detail": "Rating must be between 1 and 5."}, status=400)

        # Fetch professor
        try:
            professor = Professor.objects.get(id=professor_id)
        except Professor.DoesNotExist:
            return Response({"detail": "❌ Professor not found."}, status=404)

        # Fetch module and check if the professor is assigned
        try:
            module = Module.objects.get(code=module_code, year=year, semester=semester)
        except Module.DoesNotExist:
            return Response({"detail": "❌ Module not found for the specified year and semester."}, status=404)

        # Ensure the professor teaches this module
        if not module.professors.filter(id=professor.id).exists():
            return Response({
                "detail": f"❌ Professor {professor.name} does not teach {module.name} in {year} (Semester {semester})."
            }, status=400)

        # Check if the user has already rated this professor in this module
        existing_rating = Rating.objects.filter(user=request.user, professor=professor, module=module).exists()
        if existing_rating:
            return Response({"detail": "❌ You have already rated this professor for this module."}, status=400)

        # Save the rating
        Rating.objects.create(user=request.user, professor=professor, module=module, rating=rating)
        return Response({"message": "✅ Rating submitted successfully!"}, status=201)



# Registration API View
class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny] # Registration is public

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"}, status=200)
    
@api_view(['GET'])
def api_root(request):
    return Response({
        'modules': '/api/modules/',
        'professors': '/api/professors/',
        'ratings': '/api/ratings/{professor_id}/{module_code}/',
        'rate': '/api/rate/',
        'login': '/api/login/',
        'logout': '/api/logout/',
        'register': '/api/register/'
    })