from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, authenticate, login, logout
from .serializers import UserCreateSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.urls import reverse

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = []
    
    def create(self, request, *args, **kwargs):
        # Default API behavior
        if not request.headers.get('HX-Request'):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            return Response({
                "user": UserSerializer(user).data,
                "message": "Utilisateur créé avec succès"
            }, status=status.HTTP_201_CREATED)
        
        # HTMX request behavior - will be implemented in Django view below
        # Shouldn't actually hit this case since we're using separate views
        return Response({
            "error": "HTMX requests should use the Django view"
        }, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Default API behavior
        if not request.headers.get('HX-Request'):
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                user = User.objects.get(email=request.data['email'])
                response.data['user'] = UserSerializer(user).data
            return response
        
        # HTMX request behavior - will be implemented in Django view below
        # Shouldn't actually hit this case since we're using separate views
        return Response({
            "error": "HTMX requests should use the Django view"
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Default API behavior
        if not request.headers.get('HX-Request'):
            try:
                refresh_token = request.data["refresh"]
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
            except Exception as e:
                return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        
        # HTMX request behavior - will be implemented in Django view below
        # Shouldn't actually hit this case since we're using separate views
        return Response({
            "error": "HTMX requests should use the Django view"
        }, status=status.HTTP_400_BAD_REQUEST)

# Django Template Views
@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Extract the form data
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Basic validation
        errors = {}
        if not email:
            errors['email'] = 'Email est requis'
        if not username:
            errors['username'] = 'Nom d\'utilisateur est requis'
        if not password:
            errors['password'] = 'Mot de passe est requis'
        if password != password2:
            errors['password2'] = 'Les mots de passe ne correspondent pas'
        
        # Check if user exists
        if User.objects.filter(email=email).exists():
            errors['email'] = 'Email déjà utilisé'
        if User.objects.filter(username=username).exists():
            errors['username'] = 'Nom d\'utilisateur déjà utilisé'
            
        if errors:
            # Return the form with errors
            return render(request, 'register.html', {
                'form': {'errors': errors, 'email': {'value': email}, 'username': {'value': username},
                        'first_name': {'value': first_name}, 'last_name': {'value': last_name}}
            })
        
        # Create user
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Log the user in
        login(request, user)
        messages.success(request, 'Compte créé avec succès!')
        return redirect('dashboard')
    
    return render(request, 'register.html', {'form': {}})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect to the next parameter if available, otherwise go to dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            # Return the form with an error
            return render(request, 'login.html', {
                'form': {
                    'non_field_errors': ['Email ou mot de passe incorrect'],
                    'email': {'value': email}
                }
            })
    
    return render(request, 'login.html', {'form': {}})

@csrf_protect
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Vous avez été déconnecté.')
        return redirect('login')
    
    # If not a POST request, redirect to home page
    return redirect('dashboard')
