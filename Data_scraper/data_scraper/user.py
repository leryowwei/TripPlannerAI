class User(object):
  """ Class to produce the profile for the user """
  def __init__(self, user_input):
    # initiate variables using user input
    # make all strings lower case
    self.place = user_input['place'].lower()
    self.country = user_input['country'].lower()
    self.budget = user_input['budget']
    self.start_date = user_input['start_date']
    self.end_date = user_input['end_date']

  def days(self):
    # TODO: this will not work
    return self.end_date - self.start_date