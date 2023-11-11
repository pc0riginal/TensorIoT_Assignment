import random
import json
import boto3
import calendar
import time

# Parking lot class that holds the area of parking
class ParkingLot():
    def __init__(self,area_size,spot_size=96):
        self.size = area_size # Area size of parking
        self.spot_size = spot_size # Spot size of car
        self.total_cars = [None]*(area_size//spot_size) # Maximum cars that parks

    def map_to_json(self): 
        d = {"vehicles_with_parked_spot":{}}

        # Map license number and spot number and store into dictionary
        for s in self.total_cars:
            d["vehicles_with_parked_spot"][s._license_plate] = s.spot

        # Convert dict object to json
        j = json.dumps(d,indent=4)

        # Store into file object
        try:
            with open('parkedCars.json','w+') as f:
                f.write(j)
        except Exception as e:
            print(e)
        else:
            # If successfully store json object to file then uplod to aws s3 bucket
            s3 = boto3.client('s3')
            try:
                file_name = 'parkedCars.json'
                bucket_name = 'test101'
                object_name = str(calendar.timegm(time.gmtime()))+'_'+file_name
                
                # Call the upload_file Api with s3_client object
                response = s3.upload_file(file_name,bucket_name,object_name)
                print(response)
            except Exception as e:
                print(e)
            
# Car class to park the car in parking lot
class Car(ParkingLot):
    def __init__(self,size,license_plate_no):
        super().__init__(size)
        self._license_plate = license_plate_no
        self.spot = None

    @property
    def license_plate(self):
        return self._license_plate
    
    # Set the license plate using setter property
    @license_plate.setter
    def license_plate(self,car,license_plate_no):
        self._license_plate = license_plate_no

    # Return the license number when convert instance to str
    def __str__(self):
        return self._license_plate
    
    # Park the car on given spot based on avilability
    def park(self,total_cars,spot):
        # Check the car is already parked or not
        if not total_cars[spot]:
            self.spot = spot
            total_cars[spot] = self
            return (1,"Car with license plate [{}] parked successfully in spot [{}]".format(self.license_plate,spot))
        else:
            return (0,"Car is already Parked in the spot {}".format(spot))

# To generate the random license number and spot
def generate_random_license(size=None):

    letter = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # Generate the random 7 digit license number
    license = random.choice(letter) + random.choice(letter) + str(random.randint(10000,99999))

    # Generate the spot number between the parking lot size
    spot = random.randint(0,size-1)
    return (license,spot)

# Main function to park the car
def main_func(p):
    s = len(p.total_cars)
    total_parked_car = 0

    # Check until the parking lot is full
    while True:
        if total_parked_car < s:
            license,spot = generate_random_license(s)
            c = Car(p.size,license)
            v = c.park(p.total_cars,spot)
            if v[0]:
                total_parked_car += 1
            print(v[1])
        else:
            break

if __name__ == "__main__":
    parking_size = 2000
    p = ParkingLot(parking_size)

    # Call the main function
    main_func(p)
    
    # Call the method to upload the json file into S3 bucket 
    p.map_to_json()
