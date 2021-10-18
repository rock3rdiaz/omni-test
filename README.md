# omni-test

## Summary
This service was built using Django framework. The service use Nginx like a proxy server. ER model was design following this test instructions

## How to run locally
- Clone repository from "master" branch
- In root folder, run ```docker-compose -f docker-compose.yml -f docker-compose.local.yml up```
- The service will be running in 9999 (admin panel) and 7000 (API) port. So please go to ```http://localhost:9999/admin``` to make login (username: adminadmin, password: 123456gfdsaq). 
In this panel you can make CRUD operations in the servicies entities
- You can go to ```http://localhost:9999/silk``` to see all request sending to the service
- To test API, please import postman files inside ```postman``` folder. Load environmet variables and just make requests.
