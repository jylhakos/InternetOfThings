import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user.dart';
import '../models/api_response.dart';
import 'auth_service.dart';

// Provider for the API service
final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService(ref.read(authServiceProvider));
});

class ApiService {
  late final Dio _dio;
  final AuthService _authService;

  // API base URL - replace with your actual API Gateway URL
  static const String _baseUrl = 'https://your-api-gateway.amazonaws.com/prod';

  ApiService(this._authService) {
    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Add auth interceptor
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          final token = _authService.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (error, handler) async {
          // Handle 401 Unauthorized - token expired
          if (error.response?.statusCode == 401) {
            final refreshResult = await _authService.refreshToken();
            if (refreshResult.isSuccess) {
              // Retry the original request with new token
              final opts = error.requestOptions;
              opts.headers['Authorization'] = 'Bearer ${refreshResult.token}';
              
              try {
                final response = await _dio.fetch(opts);
                handler.resolve(response);
                return;
              } catch (e) {
                // If retry fails, continue with original error
              }
            } else {
              // If refresh fails, logout user
              await _authService.logout();
            }
          }
          handler.next(error);
        },
      ),
    );

    // Add logging interceptor for debugging
    _dio.interceptors.add(
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        logPrint: (obj) => print('[API] $obj'),
      ),
    );
  }

  // Authentication endpoints
  Future<ApiResponse<User>> login(String username, String password) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'username': username,
        'password': password,
      });

      if (response.statusCode == 200) {
        final user = User.fromJson(response.data['data']);
        return ApiResponse.success(data: user);
      } else {
        return ApiResponse.error(
          error: response.data['message'] ?? 'Login failed',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      return _handleDioError(e);
    } catch (e) {
      return ApiResponse.error(error: 'Unexpected error: $e');
    }
  }

  Future<ApiResponse<User>> register({
    required String name,
    required String phone,
    required String email,
    required String password,
  }) async {
    try {
      final response = await _dio.post('/auth/register', data: {
        'name': name,
        'phone': phone,
        'email': email,
        'password': password,
      });

      if (response.statusCode == 201) {
        final user = User.fromJson(response.data['data']);
        return ApiResponse.success(data: user, statusCode: 201);
      } else {
        return ApiResponse.error(
          error: response.data['message'] ?? 'Registration failed',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      return _handleDioError(e);
    } catch (e) {
      return ApiResponse.error(error: 'Unexpected error: $e');
    }
  }

  // User management endpoints
  Future<ApiResponse<User>> getUserProfile() async {
    try {
      final response = await _dio.get('/api/user/profile');

      if (response.statusCode == 200) {
        final user = User.fromJson(response.data['data']);
        return ApiResponse.success(data: user);
      } else {
        return ApiResponse.error(
          error: response.data['message'] ?? 'Failed to get profile',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      return _handleDioError(e);
    } catch (e) {
      return ApiResponse.error(error: 'Unexpected error: $e');
    }
  }

  Future<ApiResponse<User>> updateUserProfile({
    String? name,
    String? phone,
    String? email,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (name != null) data['name'] = name;
      if (phone != null) data['phone'] = phone;
      if (email != null) data['email'] = email;

      final response = await _dio.put('/api/user/profile', data: data);

      if (response.statusCode == 200) {
        final user = User.fromJson(response.data['data']);
        return ApiResponse.success(data: user);
      } else {
        return ApiResponse.error(
          error: response.data['message'] ?? 'Failed to update profile',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      return _handleDioError(e);
    } catch (e) {
      return ApiResponse.error(error: 'Unexpected error: $e');
    }
  }

  Future<ApiResponse<List<User>>> getUsers({
    int page = 1,
    int limit = 10,
    String? search,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'limit': limit,
      };
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }

      final response = await _dio.get('/api/users', queryParameters: queryParams);

      if (response.statusCode == 200) {
        final List<dynamic> usersJson = response.data['data'];
        final users = usersJson.map((json) => User.fromJson(json)).toList();
        return ApiResponse.success(data: users);
      } else {
        return ApiResponse.error(
          error: response.data['message'] ?? 'Failed to get users',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      return _handleDioError(e);
    } catch (e) {
      return ApiResponse.error(error: 'Unexpected error: $e');
    }
  }

  Future<ApiResponse<User>> createUser({
    required String name,
    required String phone,
    required String email,
  }) async {
    try {
      final response = await _dio.post('/api/users', data: {
        'name': name,
        'phone': phone,
        'email': email,
      });

      if (response.statusCode == 201) {
        final user = User.fromJson(response.data['data']);
        return ApiResponse.success(data: user, statusCode: 201);
      } else {
        return ApiResponse.error(
          error: response.data['message'] ?? 'Failed to create user',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      return _handleDioError(e);
    } catch (e) {
      return ApiResponse.error(error: 'Unexpected error: $e');
    }
  }

  Future<ApiResponse<void>> deleteUser(String userId) async {
    try {
      final response = await _dio.delete('/api/users/$userId');

      if (response.statusCode == 204) {
        return ApiResponse.success(data: null, statusCode: 204);
      } else {
        return ApiResponse.error(
          error: response.data['message'] ?? 'Failed to delete user',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      return _handleDioError(e);
    } catch (e) {
      return ApiResponse.error(error: 'Unexpected error: $e');
    }
  }

  // Health check endpoint
  Future<ApiResponse<Map<String, dynamic>>> healthCheck() async {
    try {
      final response = await _dio.get('/health');
      
      if (response.statusCode == 200) {
        return ApiResponse.success(data: response.data);
      } else {
        return ApiResponse.error(
          error: 'Health check failed',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      return _handleDioError(e);
    } catch (e) {
      return ApiResponse.error(error: 'Unexpected error: $e');
    }
  }

  // Error handling helper
  ApiResponse<T> _handleDioError<T>(DioException e) {
    String errorMessage;
    int statusCode = 500;

    switch (e.type) {
      case DioExceptionType.connectionTimeout:
        errorMessage = 'Connection timeout';
        break;
      case DioExceptionType.receiveTimeout:
        errorMessage = 'Receive timeout';
        break;
      case DioExceptionType.badResponse:
        statusCode = e.response?.statusCode ?? 500;
        errorMessage = e.response?.data['message'] ?? 'Server error';
        break;
      case DioExceptionType.cancel:
        errorMessage = 'Request cancelled';
        break;
      case DioExceptionType.unknown:
        errorMessage = 'Network error';
        break;
      default:
        errorMessage = 'Unknown error occurred';
    }

    return ApiResponse.error(
      error: errorMessage,
      statusCode: statusCode,
    );
  }
}
