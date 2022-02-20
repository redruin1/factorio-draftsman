
import factoriotools

def main():
    blueprint = factoriotools.Blueprint()
    blueprint.set_version(*factoriotools.__factorio_version_info__)
    
    # Checkerboard grid
    for x in range(2):
        for y in range(2):
            if (x + y) % 2 == 0:
                name = "refined-concrete"
            else:
                name = "refined-hazard-concrete-left"
            blueprint.add_tile(name, x, y)

    print(blueprint)
    pass

if __name__ == "__main__":
    main()