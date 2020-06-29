from flask import Blueprint, request, abort
from app.auth.helper import token_required
from app.customer.helper import response, response_for_created_customer, response_for_user_customer, response_with_pagination, \
    get_user_customer_json_list, paginate_customers
from app.models import User, Customer

# Initialize blueprint
customer = Blueprint('customer', __name__)


@customer.route('/customerlists/', methods=['GET'])
@token_required
def customerlist(current_user):
    """
    Return all the customers owned by the user or limit them to 10.
    Return an empty customers object if user has no customers
    :param current_user:
    :return:
    """
    user = User.get_by_id(current_user.id)
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', None, type=str)

    items, nex, pagination, previous = paginate_customers(current_user.id, page, q, user)

    if items:
        return response_with_pagination(get_user_customer_json_list(items), previous, nex, pagination.total)
    return response_with_pagination([], previous, nex, 0)


@customer.route('/customerlists/', methods=['POST'])
@token_required
def create_customerlist(current_user):
    """
    Create a Customer from the sent json data.
    :param current_user: Current User
    :return:
    """
    if request.content_type == 'application/json':
        data = request.get_json()
        name = data.get('name')
        if name:
            user_customer = Customer(name.lower(), current_user.id)
            user_customer.save()
            return response_for_created_customer(user_customer, 201)
        return response('failed', 'Missing name attribute', 400)
    return response('failed', 'Content-type must be json', 202)


@customer.route('/customerlists/<customer_id>', methods=['GET'])
@token_required
def get_customer(current_user, customer_id):
    """
    Return a user customer with the supplied user Id.
    :param current_user: User
    :param customer_id: Customer Id
    :return:
    """
    try:
        int(customer_id)
    except ValueError:
        return response('failed', 'Please provide a valid Customer Id', 400)
    else:
        user_customer = User.get_by_id(current_user.id).customers.filter_by(id=customer_id).first()
        if user_customer:
            return response_for_user_customer(user_customer.json())
        return response('failed', "Customer not found", 404)


@customer.route('/customerlists/<customer_id>', methods=['PUT'])
@token_required
def edit_customer(current_user, customer_id):
    """
    Validate the customer Id. Also check for the name attribute in the json payload.
    If the name exists update the customer with the new name.
    :param current_user: Current User
    :param customer_id: Customer Id
    :return: Http Json response
    """
    if request.content_type == 'application/json':
        data = request.get_json()
        name = data.get('name')
        if name:
            try:
                int(customer_id)
            except ValueError:
                return response('failed', 'Please provide a valid Customer Id', 400)
            user_customer = User.get_by_id(current_user.id).customers.filter_by(id=customer_id).first()
            if user_customer:
                user_customer.update(name)
                return response_for_created_customer(user_customer, 201)
            return response('failed', 'The Customer with Id ' + customer_id + ' does not exist', 404)
        return response('failed', 'No attribute or value was specified, nothing was changed', 400)
    return response('failed', 'Content-type must be json', 202)


@customer.route('/customerlists/<customer_id>', methods=['DELETE'])
@token_required
def delete_customer(current_user, customer_id):
    """
    Deleting a User Customer from the database if it exists.
    :param current_user:
    :param customer_id:
    :return:
    """
    try:
        int(customer_id)
    except ValueError:
        return response('failed', 'Please provide a valid Customer Id', 400)
    user_customer = User.get_by_id(current_user.id).customers.filter_by(id=customer_id).first()
    if not user_customer:
        abort(404)
    user_customer.delete()
    return response('success', 'Customer Deleted successfully', 200)


@customer.errorhandler(404)
def handle_404_error(e):
    """
    Return a custom message for 404 errors.
    :param e:
    :return:
    """
    return response('failed', 'Customer resource cannot be found', 404)


@customer.errorhandler(400)
def handle_400_errors(e):
    """
    Return a custom response for 400 errors.
    :param e:
    :return:
    """
    return response('failed', 'Bad Request', 400)
