from rest_framework import serializers
from .models import CustomUser


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

class VerifyOTPSerializer(serializers.Serializer):
    otp_session_id = serializers.CharField(max_length=255)
    otp_entered_by_user = serializers.CharField(max_length=6)


class UserRegistrationSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField(default='visitor')
    password = serializers.CharField(write_only=True)  # Ensure password is write-only

    class Meta:
        model = CustomUser
        fields = "__all__"

    def create(self, validated_data):
        # Remove the password from the validated data
        password = validated_data.pop('password')
        
        # Create the user without the password initially
        user = CustomUser(**validated_data)
        
        # Hash the password using set_password
        user.set_password(password)
        
        # Save the user instance
        user.save()
        
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value