import glob, uuid, sys, time
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, APIErrorException

face_client = FaceClient('<Azure Face Service Endpoint URL>',
                         CognitiveServicesCredentials('<Azure Face Service Subscription Id>'))

person_group_id = 'dystopian-future-group'
target_person_group_id = str(uuid.uuid4())

try:
    face_client.person_group.create(person_group_id=person_group_id, name=target_person_group_id)
except APIErrorException as api_error:
    print(api_error.message)

try:
    person_group_person = face_client.person_group_person.create(person_group_id, "Derek")
except APIErrorException as api_error:
    print(api_error.message)

training_images = [file for file in glob.glob('./training_pics/*.jpg')]

for training_image in training_images:
    print(f'Opening image {training_image}')
    training_image_stream = open(training_image, 'r+b')
    try:
        face_client.person_group_person.add_face_from_stream(person_group_id, person_group_person.person_id, training_image_stream)
    except APIErrorException as api_error:
        print(api_error.message)

face_client.person_group.train(person_group_id)

while (True):
    training_status = face_client.person_group.get_training_status(person_group_id)
    if (training_status.status is TrainingStatusType.succeeded):
        break
    elif (training_status.status is TrainingStatusType.failed):
        sys.exit('Training the person group has failed.')
    time.sleep(5)