from flask import make_response, jsonify, url_for
from app import app
from app.models import Customer


def response_for_user_customer(user_customer):
    """
    Return the response for when a single customer when requested by the user.
    :param user_customer:
    :return:
    """
    return make_response(jsonify({
        'status': 'success',
        'customer': user_customer
    }))


def response_for_created_customer(user_customer, status_code):
    """
    Method returning the response when a customer has been successfully created.
    :param status_code:
    :param user_customer: Customer
    :return: Http Response
    """
    return make_response(jsonify({
        'status': 'success',
        'id': user_customer.id,
        'name': user_customer.name,
        'createdAt': user_customer.create_at,
        'modifiedAt': user_customer.modified_at
    })), status_code


def response(status, message, code):
    """
    Helper method to make a http response
    :param status: Status message
    :param message: Response message
    :param code: Response status code
    :return: Http Response
    """
    return make_response(jsonify({
        'status': status,
        'message': message
    })), code


def get_user_customer_json_list(user_customers):
    """
    Make json objects of the user customers and add them to a list.
    :param user_customers: Customer
    :return:
    """
    customers = []
    for user_customer in user_customers:
        customers.append(user_customer.json())
    return customers


def response_with_pagination(customers, previous, nex, count):
    """
    Make a http response for CustomerList get requests.
    :param count: Pagination Total
    :param nex: Next page Url if it exists
    :param previous: Previous page Url if it exists
    :param customers: Customer
    :return: Http Json response
    """
    return make_response(jsonify({
        'status': 'success',
        'previous': previous,
        'next': nex,
        'count': count,
        'customers': customers
    })), 200


def paginate_customers(user_id, page, q, user):
    """
    Get a user by Id, then get hold of their customers and also paginate the results.
    There is also an option to search for a customer name if the query param is set.
    Generate previous and next pagination urls
    :param q: Query parameter
    :param user_id: User Id
    :param user: Current User
    :param page: Page number
    :return: Pagination next url, previous url and the user customers.
    """
    if q:
        pagination = Customer.query.filter(Customer.name.like("%" + q.lower().strip() + "%")).filter_by(user_id=user_id) \
            .paginate(page=page, per_page=app.config['BUCKET_AND_ITEMS_PER_PAGE'], error_out=False)
    else:
        pagination = user.customers.paginate(page=page, per_page=app.config['BUCKET_AND_ITEMS_PER_PAGE'],
                                           error_out=False)
    previous = None
    if pagination.has_prev:
        if q:
            previous = url_for('customer.customerlist', q=q, page=page - 1, _external=True)
        else:
            previous = url_for('customer.customerlist', page=page - 1, _external=True)
    nex = None
    if pagination.has_next:
        if q:
            nex = url_for('customer.customerlist', q=q, page=page + 1, _external=True)
        else:
            nex = url_for('customer.customerlist', page=page + 1, _external=True)
    items = pagination.items
    return items, nex, pagination, previous
