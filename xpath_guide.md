# Diccionario XPATH para Automatización con Selenium (SmartOLT)

## 1. Seleccionar elementos por atributos

### ID

``` xpath
//*[@id='identity']
```

### Clase parcial

``` xpath
//*[contains(@class, 'valign-center')]
```

### Atributo específico

``` xpath
//a[@href='/onu/view/xxxx']
```

------------------------------------------------------------------------

## 2. Seleccionar por texto

### Texto exacto

``` xpath
//button[text()='View']
```

### Texto parcial

``` xpath
//button[contains(., 'View')]
```

------------------------------------------------------------------------

## 3. Buscar dentro de un elemento

### Buscar `<a>` dentro de `<tr>`

``` xpath
.//a[contains(., 'View')]
```

### Cuarta columna del row

``` xpath
.//td[4]
```

------------------------------------------------------------------------

## 4. Selección por posición

### Primer row

``` xpath
(//tr[contains(@class,'valign-center')])[1]
```

### Último elemento

``` xpath
(//option)[last()]
```

------------------------------------------------------------------------

## 5. Combinar condiciones

### Clase + nombre del cliente

``` xpath
//tr[contains(@class, 'valign-center') and contains(., 'Roberto')]
```

------------------------------------------------------------------------

## 6. AND / OR

### AND

``` xpath
//a[contains(@class,'btn') and contains(.,'View')]
```

### OR

``` xpath
//span[contains(., 'CATV') or contains(., 'TV')]
```

------------------------------------------------------------------------

## 7. Navegar estructura

### Padre

``` xpath
//button[contains(., 'View')]/parent::td
```

### Hermano siguiente

``` xpath
//td[contains(., 'Roberto')]/following-sibling::td[1]
```

### Hermano anterior

``` xpath
//td[contains(., '280')]/preceding-sibling::td[2]
```

------------------------------------------------------------------------

## 8. Dentro del panel ONU

### Botón WAN Configure

``` xpath
//*[@id='wan-profile-section']//button[contains(., 'Configure')]
```

### Dropdown VLAN

``` xpath
//*[@id='wan-profile-section']//select[contains(@name,'vlan')]
```

### Speed Profile

``` xpath
//*[@id='shaper-form']//select
```

------------------------------------------------------------------------

## 9. starts-with

``` xpath
//*[starts-with(@id, 'signal_onu_')]
```

------------------------------------------------------------------------

## 10. Específicos de SmartOLT

### Icono de señal

``` xpath
//i[contains(@class, 'fa-signal')]
```

### Configured

``` xpath
//*[@id='navbar-main']//a[contains(., 'Configured')]
```

### Search bar

``` xpath
//*[@id='free_text']
```

### Reboot

``` xpath
//button[contains(., 'Reboot')]
```
