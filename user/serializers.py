from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    """ serializer for create user """
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'password', 'name']
        read_only = ['id']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 6}}
    
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class TokenSerializer(serializers.Serializer):
    """ serializer for create user token """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        """ validate authenticate user """
        email = attrs.get('email')
        password  = attrs.get('password')
        user = authenticate(request=self.context.get('request'), username=email, password=password)
        if not user:
            msg = _('Unable to authenticate with provided crendential.')
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs
