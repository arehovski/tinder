from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from tinder_app.models import User, Chat, Message


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_to_match = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password_to_match', 'email')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_to_match']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password')
        )

        return user


class UserChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_to_match = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password_to_match')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_to_match']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})
        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'description', 'profile_pic', 'subscription')

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})
        super().update(instance, validated_data)

        return instance


class UserChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(source='distance.km')
    chat = serializers.SerializerMethodField()

    def get_chat(self, instance):
        user = self.context['request'].user
        return UserChatSerializer(
            user.get_chat_id(instance),
            allow_null=True,
            read_only=True
        ).data


    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'description',
            'profile_pic', 'age', 'sex', 'distance', 'chat'
        )


class ChatUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'profile_pic')


class MessageSerializer(serializers.ModelSerializer):
    sender = ChatUserSerializer(read_only=True)

    class Meta:
        model = Message
        exclude = ('chat',)


class MessagePostSerializer(serializers.ModelSerializer):
    chat = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ('chat', 'text')

class ChatSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    latest_message = serializers.SerializerMethodField()

    def get_latest_message(self, instance):
        return MessageSerializer(
            instance.get_latest_message(),
            allow_null=True,
            read_only=True
        ).data

    class Meta:
        model = Chat
        fields = '__all__'