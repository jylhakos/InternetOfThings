import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import 'storage_service.dart';

// Provider for the auth service
final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService(ref.read(storageServiceProvider));
});

// Provider for auth state
final authStateProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(authServiceProvider));
});

class AuthService {
  final StorageService _storageService;
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'current_user';

  AuthService(this._storageService);

  bool get isLoggedIn => getCurrentUser() != null && getToken() != null;

  String? getToken() {
    return _storageService.getString(_tokenKey);
  }

  User? getCurrentUser() {
    final userJson = _storageService.getString(_userKey);
    if (userJson == null) return null;
    
    try {
      // In a real app, you'd deserialize from JSON
      // For now, returning a mock user
      return const User(
        id: '1',
        name: 'John Doe',
        phone: '+1234567890',
        email: 'john.doe@example.com',
        createdAt: 'createdAt', // Would be DateTime in real implementation
        updatedAt: 'updatedAt', // Would be DateTime in real implementation
      );
    } catch (e) {
      return null;
    }
  }

  Future<AuthResult> login(String username, String password) async {
    try {
      // Simulate API call delay
      await Future.delayed(const Duration(seconds: 2));

      // Mock authentication - in real app, call AWS Cognito
      if (username.isNotEmpty && password.length >= 6) {
        const token = 'mock_jwt_token_12345';
        const user = User(
          id: '1',
          name: 'John Doe',
          phone: '+1234567890',
          email: 'john.doe@example.com',
          createdAt: 'createdAt',
          updatedAt: 'updatedAt',
        );

        // Store token and user data
        await _storageService.setString(_tokenKey, token);
        await _storageService.setString(_userKey, 'user_json_data'); // Would store actual JSON

        return AuthResult.success(user: user, token: token);
      } else {
        return AuthResult.error('Invalid credentials');
      }
    } catch (e) {
      return AuthResult.error('Login failed: $e');
    }
  }

  Future<AuthResult> register(String name, String phone, String email, String password) async {
    try {
      // Simulate API call delay
      await Future.delayed(const Duration(seconds: 2));

      // Mock registration - in real app, call AWS Cognito
      if (name.isNotEmpty && phone.isNotEmpty && email.isNotEmpty && password.length >= 6) {
        const token = 'mock_jwt_token_12345';
        final user = User(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          name: name,
          phone: phone,
          email: email,
          createdAt: DateTime.now().toIso8601String(),
          updatedAt: DateTime.now().toIso8601String(),
        );

        // Store token and user data
        await _storageService.setString(_tokenKey, token);
        await _storageService.setString(_userKey, 'user_json_data'); // Would store actual JSON

        return AuthResult.success(user: user, token: token);
      } else {
        return AuthResult.error('Please fill all fields correctly');
      }
    } catch (e) {
      return AuthResult.error('Registration failed: $e');
    }
  }

  Future<void> logout() async {
    await _storageService.remove(_tokenKey);
    await _storageService.remove(_userKey);
  }

  Future<AuthResult> refreshToken() async {
    try {
      final currentToken = getToken();
      if (currentToken == null) {
        return AuthResult.error('No token to refresh');
      }

      // Simulate token refresh API call
      await Future.delayed(const Duration(seconds: 1));
      
      const newToken = 'refreshed_jwt_token_12345';
      await _storageService.setString(_tokenKey, newToken);

      final user = getCurrentUser();
      return AuthResult.success(user: user!, token: newToken);
    } catch (e) {
      return AuthResult.error('Token refresh failed: $e');
    }
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthService _authService;

  AuthNotifier(this._authService) : super(AuthState.initial()) {
    _checkInitialAuthState();
  }

  void _checkInitialAuthState() {
    if (_authService.isLoggedIn) {
      final user = _authService.getCurrentUser();
      final token = _authService.getToken();
      state = AuthState.authenticated(user: user!, token: token!);
    }
  }

  Future<void> login(String username, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    
    final result = await _authService.login(username, password);
    
    if (result.isSuccess) {
      state = AuthState.authenticated(
        user: result.user!,
        token: result.token!,
      );
    } else {
      state = state.copyWith(
        isLoading: false,
        error: result.error,
      );
    }
  }

  Future<void> register(String name, String phone, String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    
    final result = await _authService.register(name, phone, email, password);
    
    if (result.isSuccess) {
      state = AuthState.authenticated(
        user: result.user!,
        token: result.token!,
      );
    } else {
      state = state.copyWith(
        isLoading: false,
        error: result.error,
      );
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    state = AuthState.initial();
  }
}

class AuthState {
  final bool isLoading;
  final bool isAuthenticated;
  final User? user;
  final String? token;
  final String? error;

  const AuthState({
    required this.isLoading,
    required this.isAuthenticated,
    this.user,
    this.token,
    this.error,
  });

  factory AuthState.initial() {
    return const AuthState(
      isLoading: false,
      isAuthenticated: false,
    );
  }

  factory AuthState.authenticated({
    required User user,
    required String token,
  }) {
    return AuthState(
      isLoading: false,
      isAuthenticated: true,
      user: user,
      token: token,
    );
  }

  AuthState copyWith({
    bool? isLoading,
    bool? isAuthenticated,
    User? user,
    String? token,
    String? error,
  }) {
    return AuthState(
      isLoading: isLoading ?? this.isLoading,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      user: user ?? this.user,
      token: token ?? this.token,
      error: error ?? this.error,
    );
  }
}

class AuthResult {
  final bool isSuccess;
  final User? user;
  final String? token;
  final String? error;

  const AuthResult._({
    required this.isSuccess,
    this.user,
    this.token,
    this.error,
  });

  factory AuthResult.success({
    required User user,
    required String token,
  }) {
    return AuthResult._(
      isSuccess: true,
      user: user,
      token: token,
    );
  }

  factory AuthResult.error(String error) {
    return AuthResult._(
      isSuccess: false,
      error: error,
    );
  }
}
