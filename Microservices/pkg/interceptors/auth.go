package interceptors

import (
	"context"
	"strings"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"

	authpb "auth-service/proto"
)

type AuthInterceptor struct {
	authClient authpb.AuthServiceClient
}

func NewAuthInterceptor(authClient authpb.AuthServiceClient) *AuthInterceptor {
	return &AuthInterceptor{authClient: authClient}
}

func (a *AuthInterceptor) Unary() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req interface{},
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (interface{}, error) {
		// Skip authentication for health checks
		if strings.HasSuffix(info.FullMethod, "Health/Check") {
			return handler(ctx, req)
		}

		if err := a.authorize(ctx); err != nil {
			return nil, err
		}

		return handler(ctx, req)
	}
}

func (a *AuthInterceptor) authorize(ctx context.Context) error {
	md, ok := metadata.FromIncomingContext(ctx)
	if !ok {
		return status.Error(codes.Unauthenticated, "metadata not provided")
	}

	values := md.Get("authorization")
	if len(values) == 0 {
		return status.Error(codes.Unauthenticated, "authorization token not provided")
	}

	token := strings.TrimPrefix(values[0], "Bearer ")
	resp, err := a.authClient.ValidateToken(ctx, &authpb.ValidateTokenRequest{
		Token: token,
	})
	if err != nil {
		return status.Error(codes.Unauthenticated, "failed to validate token")
	}

	if !resp.Valid {
		return status.Error(codes.Unauthenticated, "invalid token")
	}

	return nil
}