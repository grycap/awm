from connexion import request
from awm.models.allocation_info import AllocationInfo
from awm.models.allocation import Allocation
from awm.models.eosc_node_environment import EoscNodeEnvironment
from awm.models.credentials_open_stack import CredentialsOpenStack
from awm.models.credentials_kubernetes import CredentialsKubernetes
from awm.models.page_of_allocations import PageOfAllocations
from awm.models.success import Success


def delete_allocation(allocation_id):
    """Delete existing credentials or EOSC environment of the user

    :rtype: Success
    """
    # @TODO: delete the allocation from the Database
    msg = Success(message=f"Allocation {allocation_id} deleted successfully")
    return msg.to_dict(), 204


def get_allocation_info(allocation_id):
    """Retrieve information about existing credentials or EOSC environment of the user

    :rtype: AllocationInfo
    """
    # @TODO: get the allocation from the Database
    allocation = AllocationInfo(_id=allocation_id, allocation=EoscNodeEnvironment(node_name="node_name"))
    return allocation.to_dict()


def list_allocations(all_nodes, from_=None, limit=None):
    """List all credentials or EOSC environments of the user


    :param all_nodes: Return allocations from all nodes
    :type all_nodes: bool
    :param _from: Index of the first element to return
    :type _from: int
    :param limit: Maximum number of elements to return
    :type limit: int

    :rtype: PageOfAllocations
    """
    # @TODO: get the allocations from the Database
    all = []
    for i in range(0, 15):
        allocation = CredentialsOpenStack(host="host")
        url = f"{request.base_url}{request.url.path[1:]}/{i}"
        all.append(AllocationInfo(_id=str(i), allocation=allocation, _self=url))

    page = PageOfAllocations(_from=from_, limit=limit, elements=all[from_:from_ + limit], count=len(all))
    return page.to_dict()


def record_allocation(body):
    """Record credentials or EOSC environment of the user

    :param body: Allocation information
    :type body: dict | bytes

    :rtype: AllocationId
    """
    # @TODO: add the allocation to the Database
    new_allocation = Allocation.from_dict(body)
    return 'do some magic!'


def update_allocation(body):
    """Update existing credentials or EOSC environment of the user

    :param body: Allocation information
    :type body: dict | bytes

    :rtype: AllocationInfo
    """
    # @TODO: update the allocation from the Database
    new_allocation = Allocation.from_dict(body)
    return 'do some magic!'
