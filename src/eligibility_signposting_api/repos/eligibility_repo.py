import logging
from typing import Annotated, Any

from boto3.resources.base import ServiceResource
from wireup import Inject, service

from eligibility_signposting_api.model.eligibility import NHSNumber
from eligibility_signposting_api.model.person import Person
from eligibility_signposting_api.repos.exceptions import NotFoundError

logger = logging.getLogger(__name__)


@service(qualifier="eligibility_table")
def eligibility_table_factory(dynamodb_resource: Annotated[ServiceResource, Inject(qualifier="dynamodb")]) -> Any:
    table = dynamodb_resource.Table("People")  # type: ignore[reportAttributeAccessIssue]
    logger.info("eligibility_table %r", table, extra={"table": table})
    return table


@service
class EligibilityRepo:
    def __init__(self, table: Annotated[Any, Inject(qualifier="eligibility_table")]) -> None:
        super().__init__()
        self.table = table

    def get_person(self, nhs_number: NHSNumber) -> Person:
        response = self.table.get_item(
            Key={"NHS_NUMBER": f"PERSON#{nhs_number}", "ATTRIBUTE_TYPE": f"PERSON#{nhs_number}"}
        )
        logger.debug("response %r for %r", response, nhs_number, extra={"response": response, "nhs_number": nhs_number})

        if "Item" not in response:
            message = f"Person not found with nhs_number {nhs_number}"
            raise NotFoundError(message)

        person = response.get("Item")
        logger.debug("returning person %s", person, extra={"person": person})
        return person
