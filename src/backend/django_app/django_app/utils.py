from .exception_handler import CustomAPIException

def validate_or_raise(serializer,status_code,message):
    if not serializer.is_valid():
        raise CustomAPIException(
            detail=serializer.errors,
            status_code=status_code,
            message=message
        )
    return serializer.validated_data
