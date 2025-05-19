# Smartphone-Based Fall Detection System for the Elderly

## Introduction

Falls represent one of the most significant risks for the elderly population. Enhancing the care and quality of life for these individuals can be achieved through the adoption of a fall detection system. This project presents a smartphone-based application that utilizes accelerometer and gyroscope data to detect falls and send a request to a nursing agency, enabling intervention and necessary care. The system also proposes mechanisms to ignore and filter out false positives, ensuring the reliability of the detections.

This project draws inspiration and shares conceptual similarities with the [SensorServer repository](https://github.com/umer0586/SensorServer) by umer0586, particularly in its approach to handling sensor data and server-side processing for real-time analysis.

## Theoretical Background

Falls are the second leading cause of accidental deaths worldwide. Annually, approximately 37.3 million severe injuries require medical attention [1]. The risk of falls primarily affects individuals with impaired balance, such as the elderly, amputees, sedentary individuals, and people with neurological disabilities [2]. Fall detection involves the use of sensors to monitor changes in posture and movement dynamics, distinguishing normal daily activities from accidental fall events.

The advancement of smartphones and their integrated sensors has enabled the development of mobile health monitoring solutions. Sensors such as accelerometers and gyroscopes, commonly found in mobile devices, allow for the collection of motion data that can be analyzed by algorithms to identify falls.

Furthermore, the widespread adoption of smartphones allows a large number of people to benefit from this technology without the need to purchase additional equipment, making elderly safety more accessible and simplified.

## Methodology

For the realization of this study, an Android smartphone running an application capable of capturing accelerometer and gyroscope data will be employed. The collected data will be processed and sent to a remote server, where it will be analyzed and classified to identify characteristic fall patterns. The system will incorporate machine learning algorithms with the aim of distinguishing and discarding false positives.

### Infrastructure Details:

* **Devices used:** Android smartphone equipped with accelerometer and gyroscope.
* **Infrastructure and communication:** The application will communicate data via HTTP protocol to a remote server, implemented using a REST architecture.
* **Processing server:** A server developed in Python will receive the data and apply a machine learning model trained for fall detection, responsible for triggering an alert to the nursing agency upon positive detection.
* **Data storage:** Raw data and detection information will be stored in CSV format for future analysis and continuous improvement of the machine learning model.

### Diagram 1 - System Connection

```mermaid
graph LR
    A[Smartphone_Acc_Gyro] --> B(Remote_Server_Python_REST);
    B -- HTTP_Data --> C{Neural_Network_ML_Model};
    C -- Query_DB --> D[Database_CSV];
    D -- Analyze_Data --> C;
    C -- Alert_No_Alert --> B;
    B -- Alert --> E(Nursing_Agency);
    B -- Update_DB --> D;
