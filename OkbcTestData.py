
Eats   = create_slot('Eats')
Age    = create_slot('Age')
Weight = create_slot('Weight')
BirthTime = create_slot('BirthTime',pretty_name = 'Birth Time')

Thing  = create_class('Thing')

Food   = create_class('Food',direct_superclasses = [Thing])

Grains = create_class('Grains',direct_superclasses = [Food])
DairyProducts = create_class('DairyProducts',direct_superclasses = [Food])
Meats = create_class('Meats',direct_superclasses = [Food])
Vegetables = create_class('Vegetables',direct_superclasses = [Food])

Berry = create_class('Berry',direct_superclasses = [Food])
Cookie = create_class('Cookie',direct_superclasses = [Food])
Apple = create_class('Apple',direct_superclasses = [Food])
Toast = create_class('Toast',direct_superclasses = [Food])

Agent  = create_class('Agent',direct_superclasses = [Thing])
Human = create_class('Human',direct_superclasses = [Agent],
                      template_slots = [[Eats,
                                         Grains,
                                         Vegetables,
                                         DairyProducts,
                                         Meats]])
Child  = create_class('Child',
                      direct_superclasses = [Human])

AdultHuman  = create_class('AdultHuman',
                           direct_superclasses = [Human])

Ethan = create_individual('Ethan',
                          direct_types=[Child],
                          own_slots = [[Age,2],
                                       [BirthTime,'1999-11-04 GMT-6'],
                                       [Eats,
                                        Toast,
                                        Cookie]],
                          pretty_name = 'Ethan Brown')

Sam = create_individual('Sam',
                        direct_types=[Child],
                        own_slots = [[Age,2],
                                     [BirthTime,'1999-11-07 16:30 GMT-6'],
                                     [Eats,
                                      Apple,
                                      Berry,
                                      Cookie]],
                        pretty_name = 'Samuel Francesco Aiudi-Murphy')

Shawn = create_individual('Shawn',
                          direct_types=[AdultHuman],
                          own_slots = [[Age,38],
                                       [BirthTime,'1964-07-25 01:15 GMT-5'],
                                       [Eats,
                                        Apple,
                                        Berry,
                                        Cookie]],
                        pretty_name = 'Shawn Francis Murphy')


