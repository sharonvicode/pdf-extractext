"""
Controlador de usuarios - Capa de presentación.

Este módulo actúa como intermediario entre las rutas HTTP
y los servicios de negocio, manejando la conversión de datos.
"""

from typing import List

from fastapi import HTTPException, status

from models.user import User, UserCreate, UserResponse, UserUpdate
from services.user_service import UserService


class UserController:
    """
    Controlador para operaciones de usuarios.

    Maneja las peticiones HTTP relacionadas con usuarios,
    validando entradas y formateando respuestas.

    Attributes:
        _service: Instancia del servicio de usuarios.
    """

    def __init__(self, service: UserService):
        """
        Inicializa el controlador con el servicio.

        Args:
            service: Instancia de UserService.
        """
        self._service = service

    def get_all_users(self) -> List[UserResponse]:
        """
        Obtiene todos los usuarios.

        Returns:
            Lista de usuarios en formato de respuesta.
        """
        users = self._service.get_all()
        return [self._to_response(user) for user in users]

    def get_user_by_id(self, user_id: int) -> UserResponse:
        """
        Obtiene un usuario por ID.

        Args:
            user_id: ID del usuario.

        Returns:
            Usuario en formato de respuesta.

        Raises:
            HTTPException: Si el usuario no existe.
        """
        user = self._service.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id {user_id} no encontrado",
            )
        return self._to_response(user)

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Crea un nuevo usuario.

        Args:
            user_data: Datos del usuario a crear.

        Returns:
            Usuario creado en formato de respuesta.

        Raises:
            HTTPException: Si hay error de validación.
        """
        try:
            user = self._service.create(user_data)
            return self._to_response(user)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        """
        Actualiza un usuario existente.

        Args:
            user_id: ID del usuario a actualizar.
            user_data: Datos a actualizar.

        Returns:
            Usuario actualizado en formato de respuesta.

        Raises:
            HTTPException: Si el usuario no existe o hay error de validación.
        """
        try:
            user = self._service.update(user_id, user_data)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Usuario con id {user_id} no encontrado",
                )
            return self._to_response(user)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def delete_user(self, user_id: int) -> dict:
        """
        Elimina un usuario.

        Args:
            user_id: ID del usuario a eliminar.

        Returns:
            Mensaje de confirmación.

        Raises:
            HTTPException: Si el usuario no existe.
        """
        deleted = self._service.delete(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id {user_id} no encontrado",
            )
        return {"message": f"Usuario {user_id} eliminado correctamente"}

    def _to_response(self, user: User) -> UserResponse:
        """
        Convierte un User a UserResponse.

        Args:
            user: Entidad User.

        Returns:
            UserResponse formateado.
        """
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
        )
