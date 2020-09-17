# Backend test

## What is done

- Implemented `setUserTrialPeriod` and `removeUserTrialPeriod` to set or remove trial period for a user. The trial period is set for 7 days, either in the future or in the past. The past is for the test purposes.
- Adjusted `getUserInfo` to return timestamp of the end of the trial period, if the trial period is set.
- Extended the `pyTests` to cover new use cases:
  ```python
  tests/test_session.py::test_set_trial_not_global_admin PASSED                                                                                                                     [ 60%]
  tests/test_session.py::test_delete_trial_not_global_admin PASSED                                                                                                                  [ 70%]
  tests/test_session.py::test_trial_period_timestamp PASSED                                                                                                                         [ 80%]
  tests/test_session.py::test_trial_period_not_expired PASSED                                                                                                                       [ 90%]
  tests/test_session.py::test_trial_period_expired PASSED  
  ```
- Extended `OpenAPI` specification to cover new use cases including request and response schemas.
  ![user-trial-put](https://user-images.githubusercontent.com/23406415/93450793-ac8f8c80-f8d6-11ea-9a9b-037223e4dc9d.png)
  ![user-trial-delete](https://user-images.githubusercontent.com/23406415/93450785-a9949c00-f8d6-11ea-9710-f31e3a4415d0.png)

## What is missing
- When the trial period ends, the user is not allowed to access only 2 endpoints, `updateUser` and `getUserInfo`. I wasn't able to make it as a middleware for every request.
- I didn't manage to complete the last optional point. I am not familiar with `Alembic migration` yet.
