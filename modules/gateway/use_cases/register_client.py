from core.security.ca import IssuedCertificate, PrivateCA
from modules.gateway.domain.entities import ClientType, RegisteredClientEntity
from modules.gateway.domain.interfaces import IRegisteredClientRepository


class RegisterClientUseCase:
    """Issues a private mTLS client certificate and registers the client identity."""

    def __init__(
        self,
        client_repo: IRegisteredClientRepository,
        ca: PrivateCA,
    ) -> None:
        self.client_repo = client_repo
        self.ca = ca

    async def execute(
        self,
        name: str,
        client_type: ClientType,
        owner_id: str,
        validity_days: int = 30,
    ) -> tuple[RegisteredClientEntity, IssuedCertificate]:
        cn = f"{client_type.value.lower()}:{owner_id}:{name}"
        issued = self.ca.issue_client_certificate(
            common_name=cn, validity_days=validity_days
        )

        client = await self.client_repo.create(
            name=name,
            client_type=client_type,
            owner_id=owner_id,
            cert_fingerprint=issued.fingerprint,
            cert_serial=issued.serial,
            expires_at=issued.expires_at,
        )
        return client, issued
