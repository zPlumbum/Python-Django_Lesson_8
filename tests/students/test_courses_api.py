import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from students.models import Course


@pytest.mark.django_db
def test_courses_get(api_client, course_factory):
    # arrange
    course = course_factory()
    url = reverse('courses-detail', args=[course.id])

    # act
    response = api_client.get(url)

    # assert
    assert response.status_code == HTTP_200_OK
    response_json = response.json()
    assert response_json
    assert response_json['id'] == course.id
    assert response_json['name'] == course.name


@pytest.mark.django_db
def test_courses_list(api_client, course_factory):
    # arrange
    course1 = course_factory()
    course2 = course_factory()
    url = reverse('courses-list')

    # act
    response = api_client.get(url)

    # assert
    assert response.status_code == HTTP_200_OK

    response_json = response.json()
    assert len(response_json) == 2

    result_ids = {course['id'] for course in response_json}
    assert {course1.id, course2.id} == result_ids


@pytest.mark.django_db
def test_courses_filter_id(api_client, course_factory):
    # arrange
    course1 = course_factory()
    course2 = course_factory()
    url = reverse('courses-list')

    # act
    response = api_client.get(url, {'id': course1.id})

    # assert
    assert response.status_code == HTTP_200_OK

    response_json = response.json()
    assert len(response_json) == 1

    result = response_json[0]
    assert result['id'] == course1.id


@pytest.mark.django_db
def test_courses_filter_name(api_client):
    # arrange
    course1 = Course.objects.create(name='physics')
    course2 = Course.objects.create(name='physical biology')
    url = reverse('courses-list')

    # act
    response = api_client.get(url, {'name': 'biology'})

    # assert
    assert response.status_code == HTTP_200_OK

    response_json = response.json()
    assert len(response_json) == 1

    result = response_json[0]
    assert result['name'] == course2.name


@pytest.mark.parametrize(
    ['name', 'status_code'],
    (
            ('programming', HTTP_201_CREATED),
            ('java', HTTP_201_CREATED),
            ('python', HTTP_201_CREATED),
    )
)
@pytest.mark.django_db
def test_courses_create(api_client, name, status_code):
    # arrange
    url = reverse('courses-list')
    course_payload = {
        'name': name
    }

    # act
    response = api_client.post(url, course_payload)
    created_course = Course.objects.all().filter(name=name)

    # assert
    assert response.json()['name'] == name
    assert response.status_code == status_code
    assert created_course


@pytest.mark.django_db
def test_courses_update(api_client, course_factory):
    # arrange
    course = course_factory()
    url_create = reverse('courses-list')
    course_payload = {
        'name': course.name
    }
    url_update = reverse('courses-detail', args=[course.id])
    course_payload_update = {
        'name': 'Example name'
    }

    # act
    response = api_client.post(url_create, course_payload)
    response_update = api_client.patch(url_update, course_payload_update)
    updated_course = Course.objects.all().filter(name=course_payload_update['name'])

    # assert
    assert response.status_code == HTTP_201_CREATED
    assert response.json()['name'] == course_payload['name']

    assert response_update.status_code == HTTP_200_OK
    assert response_update.json()['name'] == course_payload_update['name']
    assert updated_course


@pytest.mark.django_db
def test_courses_delete(api_client, course_factory):
    # arrange
    course = course_factory()
    url_delete = reverse('courses-detail', args=[course.id])

    # act
    response_delete = api_client.delete(url_delete)
    deleted_course = Course.objects.all().filter(id=course.id)

    # assert
    assert response_delete.status_code == HTTP_204_NO_CONTENT
    assert not deleted_course


# Дополнительное задание
@pytest.mark.parametrize(
    ['students_amount', 'message'],
    (
            (14, 'Допустимое кол-во студентов'),
            (25, 'Недопустимое кол-во студентов'),
            (20, 'Допустимое кол-во студентов'),
            (21, 'Недопустимое кол-во студентов'),
    )
)
@pytest.mark.django_db
def test_max_students(settings, students_amount, message):
    if students_amount <= settings.MAX_STUDENTS_PER_COURSE:
        answer = 'Допустимое кол-во студентов'
    else:
        answer = 'Недопустимое кол-во студентов'

    assert answer == message
