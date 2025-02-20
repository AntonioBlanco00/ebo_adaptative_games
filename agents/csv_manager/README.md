# csv_manager
Agente que tras recibir una señal de actualización (a través de marcar como True su atributo actualizar_info), recoge toda la información que tiene almacenada del juego y usuario actual, y la actualiza en el csv que ejerce como base de datos.


## Configuration parameters
As any other component, *csv_manager* needs a configuration file to start. In
```
etc/config
```
you can find an example of a configuration file. We can find there the following lines:
```
EXAMPLE HERE
```

## Starting the component
To avoid changing the *config* file in the repository, we can copy it to the component's home directory, so changes will remain untouched by future git pulls:

```
cd <csv_manager's path> 
```
```
cp etc/config config
```

After editing the new config file we can run the component:

```
bin/csv_manager config
```
