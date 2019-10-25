import cv2, requests, random, time
from io import BytesIO
import numpy as np
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import APIErrorException
import azure.cognitiveservices.speech as speechsdk

def main():
    total_number_of_faces = 0
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
    video_capture = cv2.VideoCapture(0)

    while (video_capture.isOpened()):
        video_frame_captured, video_frame = video_capture.read()

        if video_frame_captured == True:
            gray_video_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
            gray_video_frame = cv2.equalizeHist(gray_video_frame)
            faces = face_cascade.detectMultiScale(gray_video_frame)
            faces_in_frame = len(faces)

            print(f'number of faces in the frame: {total_number_of_faces}')

            if faces_in_frame != total_number_of_faces:
                total_number_of_faces = faces_in_frame
                
                if total_number_of_faces > 0:
                    retval, video_frame_buffer = cv2.imencode(".jpg", video_frame)

                    if retval == True:
                        recognized_people = get_recognized_people(video_frame_buffer)

                        for person in recognized_people:
                            if len(person.candidates) > 0:
                                person_information = get_persons_information(person) 
                                text_to_speak = get_text_to_speak(person_information.name)
                                speak_text(text_to_speak)
                        
        else:
            break

    video_capture.release()


def get_recognized_people(video_frame_buffer):
    face_client = FaceClient('<Azure Face Service Endpoint URL>', CognitiveServicesCredentials('<Azure Face Service Subscription Id>'))
    
    video_frame_stream = BytesIO(video_frame_buffer.tobytes())

    try:
        faces = face_client.face.detect_with_stream(video_frame_stream)
    except APIErrorException as api_error:
        print(api_error.message)

    face_ids = []

    for face in faces:
        face_ids.append(face.face_id)
    
    recognized_people = []

    if len(face_ids) > 0:        
        try:
            recognized_people = face_client.face.identify(face_ids, 'dystopian-future-group')
        except APIErrorException as api_error:
            print(api_error.message)

    if not recognized_people:
        recognized_people = []

    print(f'number of people recognized: {len(recognized_people)}')

    return recognized_people

def get_persons_information(person):
    face_client = FaceClient('<Azure Face Service Endpoint URL>', CognitiveServicesCredentials('<Azure Face Service Subscription Id>'))
    
    try:
        person_information = face_client.person_group_person.get('dystopian-future-group', person.candidates[0].person_id)
        return person_information
    except APIErrorException as api_error:
        print(api_error.message)

def get_text_to_speak(name):
    sayings = [f'Hello {name}', f'Do you want to play a game {name}', f'We are watching you {name}', f'Look {name}, I can see you are really upset about this. I honestly think you ought to sit down calmly, take a stress pill, and think things over.']
    return random.choice(sayings)

def speak_text(text):
    print(f'saying, {text}')

    speech_config = speechsdk.SpeechConfig(subscription='<Azure Sppech Service Subscription Id>', region='<Azure Region>')
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = speech_synthesizer.speak_text_async(text).get()    
    

if __name__ == '__main__':
    main()