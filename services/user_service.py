"""
Servicio de usuarios - Lógica de negocio.

Este módulo contiene la lógica de negocio para operaciones
de usuarios, separada de la capa de presentación.
"""

from datetime import datetime
from typing import List, Optional

from models.user import User, UserCreate, UserUpdate


class UserService:
    """
    Servicio para operaciones de usuarios.

    Encapsula las reglas de negocio y operaciones CRUD
    para el recurso User.

    Attributes:
        _users: Lista en memoria de usuarios (simulación de base de datos).
        _next_id: Contador para generar IDs únicos.
    """

    def __init__(self):
        """Inicializa el servicio con datos de ejemplo."""
        self._users: List[User] = []
        self._next_id: int = 1
        self._seed_data()

    def _seed_data(self) -> None:
        """Carga datos iniciales de ejemplo."""
        sample_users = [
            UserCreate(email="usuario@ejemplo.com", full_name="Usuario Ejemplo"),
            UserCreate(email="admin@ejemplo.com", full_name="Administrador Sistema"),
        ]
        for user_data in sample_users:
            self.create(user_data)

    def get_all(self) -> List[User]:
        """
        Obtiene todos los usuarios activos.

        Returns:
            Lista de usuarios ordenados por ID.
        """
        return sorted(self._users, key=lambda u: u.id)

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Busca un usuario por su ID.

        Args:
            user_id: ID del usuario a buscar.

        Returns:
            El usuario encontrado o None si no existe.
        """
        return next((user for user in self._users if user.id == user_id), None)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Busca un usuario por su email.

        Args:
            email: Email del usuario a buscar.

        Returns:
            El usuario encontrado o None si no existe.
        """
        return next((user for user in self._users if user.email == email), None)

    def create(self, user_data: UserCreate) -> User:
        """
        Crea un nuevo usuario.

        Args:
            user_data: Datos del usuario a crear.

        Returns:
            El usuario creado.

        Raises:
            ValueError: Si el email ya está registrado.
        """
        if self.get_by_email(user_data.email):
            raise ValueError(f"Email '{user_data.email}' ya está registrado")

        new_user = User(
            id=self._next_id,
            email=user_data.email,
            full_name=user_data.full_name,
            is_active=user_data.is_active,
            created_at=datetime.now(),
            updated_at=None,
        )

        self._users.append(new_user)
        self._next_id += 1

        return new_user

    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Actualiza un usuario existente.

        Args:
            user_id: ID del usuario a actualizar.
            user_data: Datos a actualizar.

        Returns:
            El usuario actualizado o None si no existe.

        Raises:
            ValueError: Si el nuevo email ya está registrado.
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        # Verificar email único si se está actualizando
        if user_data.email and user_data.email != user.email:
            if self.get_by_email(user_data.email):
                raise ValueError(f"Email '{user_data.email}' ya está registrado")

        # Actualizar campos
        updated_user = User(
            id=user.id,
            email=user_data.email or user.email,
            full_name=user_data.full_name or user.full_name,
            is_active=user_data.is_active
            if user_data.is_active is not None
            else user.is_active,
            created_at=user.created_at,
            updated_at=datetime.now(),
        )

        # Reemplazar en la lista
        index = self._users.index(user)
        self._users[index] = updated_user

        return updated_user

    def delete(self, user_id: int) -> bool:
        """
        Elimina un usuario por su ID.

        Args:
            user_id: ID del usuario a eliminar.

        Returns:
            True si se eliminó, False si no existía.
        """
        user = self.get_by_id(user_id)
        if user:
            self._users.remove(user)
            return True
        return False
