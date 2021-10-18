from models import rulet

r = rulet.Rulet()
spins = r.spin()
b = [i for i in next(spins)] + [i for i in next(spins)]
print(b)