from rest_framework import serializers

from .models import Habit, HabitCompletion


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ["owner", "created_at", "updated_at"]

    def validate(self, data):
        related_habit = data.get("related_habit")
        is_enjoyable = data.get("is_enjoyable")
        reward = data.get("reward")

        if (related_habit is not None) and reward and (not is_enjoyable):
            raise serializers.ValidationError(
                {
                    "is_enjoyable": "У полезной привычки не может быть связанной и вознаграждения одновременно"
                }
            )

        if (is_enjoyable is True) and reward:
            raise serializers.ValidationError({"is_enjoyable": "У приятной привычки не может быть вознаграждения"})

        if (is_enjoyable is True) & (related_habit is not None):
            raise serializers.ValidationError({"is_enjoyable": "У приятной привычки не может быть связанной привычки"})

        if related_habit is not None and not related_habit.is_enjoyable:
            raise serializers.ValidationError({"related_habit": "Связанной привычкой может быть только приятная."})

        return data


class HabitCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitCompletion
        fields = ["id", "habit", "completed_at", "is_completed", "note"]
        read_only_fields = ["id", "completed_at"]

    def validate(self, data):
        habit = data.get("habit")
        request = self.context.get("request")
        if request.user != habit.owner:
            raise serializers.ValidationError({"habit": "Нельзя присваивать завершенной привычке чужую привычку"})
        return data
