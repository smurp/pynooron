create_slot('Eats')
create_slot('Age')
create_slot('Weight')
create_slot('BirthTime',
            pretty_name='Birth Time')
create_class('Thing')
create_class('Food',
             direct_superclasses=['Thing'])
create_class('Grains',
             direct_superclasses=['Food'])
create_class('DairyProducts',
             direct_superclasses=['Food'])
create_class('Meats',
             direct_superclasses=['Food'])
create_class('Vegetables',
             direct_superclasses=['Food'])
create_class('Berry',
             direct_superclasses=['Food'])
create_class('Cookie',
             direct_superclasses=['Food'])
create_class('Apple',
             direct_superclasses=['Food'])
create_class('Toast',
             direct_superclasses=['Food'])
create_class('Agent',
             direct_superclasses=['Thing'])
create_class('Human',
             direct_superclasses=['Agent'],
             template_slots=[['Eats', 'Grains', 'Vegetables', 'DairyProducts', 'Meats'],
                            ])
create_class('Child',
             direct_superclasses=['Human'])
create_class('AdultHuman',
             direct_superclasses=['Human'])
create_individual('Ethan',
                  direct_types=['Child'],
                  own_slots=[['Eats', 'Toast', 'Cookie'],
                             ['Age', 2],
                             ['BirthTime', '1999-11-04 GMT-6'],
                            ],
                  pretty_name='Ethan Brown')
create_individual('Sam',
                  direct_types=['Child'],
                  own_slots=[['Eats', 'Apple', 'Berry', 'Cookie'],
                             ['Age', 2],
                             ['BirthTime', '1999-11-07 16:30 GMT-6'],
                            ],
                  pretty_name='Samuel Francesco Aiudi-Murphy')
create_individual('Shawn',
                  direct_types=['AdultHuman'],
                  own_slots=[['Eats', 'Apple', 'Berry', 'Cookie'],
                             ['Age', 38],
                             ['BirthTime', '1964-07-25 01:15 GMT-5'],
                            ],
                  pretty_name='Shawn Francis Murphy')
