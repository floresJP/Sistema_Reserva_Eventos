```sql
-- Eliminar tablas si ya existen (orden importante por FK: de la mas
-- dependiente a la menos dependiente)
DROP TABLE IF EXISTS cuota;
DROP TABLE IF EXISTS pago;
DROP TABLE IF EXISTS servicio_adicional;
DROP TABLE IF EXISTS reserva;
DROP TABLE IF EXISTS tematica;
DROP TABLE IF EXISTS cliente;

-- =============================================
-- TABLA: cliente
-- id_cliente es VARCHAR(4) (no SERIAL) porque el codigo lo genera
-- GeneradorID en Python con formato prefijo + 3 digitos (ej. "C001").
-- =============================================
CREATE TABLE cliente (
    id_cliente     VARCHAR(4)  PRIMARY KEY,
    nombre         VARCHAR(40) NOT NULL,
    apellido       VARCHAR(60) NOT NULL,
    dni            VARCHAR(8)  NOT NULL,
    telefono       VARCHAR(9)  NOT NULL,
    correo         VARCHAR(50) NOT NULL UNIQUE,
    fecha_registro DATE        NOT NULL
);

-- =============================================
-- TABLA: tematica
-- =============================================
CREATE TABLE tematica (
    id_tematica VARCHAR(4)    PRIMARY KEY,
    descripcion TEXT          NOT NULL,
    precio_base NUMERIC(10,2) NOT NULL,
    estado      VARCHAR(20)   NOT NULL
);

-- =============================================
-- TABLA: reserva
-- =============================================
CREATE TABLE reserva (
    id_reserva       VARCHAR(4)  PRIMARY KEY,
    fecha_reserva    DATE        NOT NULL,
    fecha_evento     DATE        NOT NULL,
    hora_inicio      TIME(0)     NOT NULL,
    hora_fin         TIME(0)     NOT NULL,
    direccion        VARCHAR(90) NOT NULL,
    edad_cumpleanero INT         NULL,
    observaciones    TEXT        NULL,
    estado           VARCHAR(20) NOT NULL,
    id_cliente       VARCHAR(4)  NOT NULL REFERENCES cliente(id_cliente),
    id_tematica      VARCHAR(4)  NOT NULL REFERENCES tematica(id_tematica)
);

-- =============================================
-- TABLA: servicio_adicional
-- =============================================
CREATE TABLE servicio_adicional (
    id_servicio_adicional     VARCHAR(4)    PRIMARY KEY,
    nombre_servicio_adicional VARCHAR(50)   NOT NULL,
    descripcion                TEXT          NOT NULL,
    precio                     NUMERIC(10,2) NOT NULL,
    estado                     VARCHAR(20)   NOT NULL,
    id_reserva                 VARCHAR(4)    NOT NULL REFERENCES reserva(id_reserva)
);

-- =============================================
-- TABLA: pago
-- =============================================
CREATE TABLE pago (
    id_pago      VARCHAR(4)    PRIMARY KEY,
    fecha_pago   DATE          NOT NULL,
    monto_total  NUMERIC(10,2) NOT NULL,
    metodo_pago  VARCHAR(30)   NOT NULL,
    estado_pago  VARCHAR(30)   NOT NULL,
    total_cuotas INT           NOT NULL,
    id_reserva   VARCHAR(4)    NOT NULL REFERENCES reserva(id_reserva)
);

-- =============================================
-- TABLA: cuota
-- =============================================
CREATE TABLE cuota (
    id_cuota          VARCHAR(4)    PRIMARY KEY,
    numero_cuota      INT           NOT NULL,
    monto             NUMERIC(10,2) NOT NULL,
    fecha_vencimiento DATE          NOT NULL,
    fecha_pago        DATE          NULL,
    estado            VARCHAR(20)   NOT NULL,
    id_pago            VARCHAR(4)    NOT NULL REFERENCES pago(id_pago)
);

-- =============================================
-- DATOS DE PRUEBA
-- =============================================
INSERT INTO cliente (id_cliente, nombre, apellido, dni, telefono, correo, fecha_registro) VALUES
('C001','Lucía','Ramírez Torres','74512301','987654321','lucia.ramirez@gmail.com','2024-01-10'),
('C002','Carlos','Mendoza Quispe','65423187','976543210','carlos.mendoza@hotmail.com','2024-02-14'),
('C003','Valeria','Flores Sánchez','72398461','965432109','valeria.flores@gmail.com','2024-03-05'),
('C004','Diego','Chávez Llerena','80123456','954321098','diego.chavez@outlook.com','2024-03-20'),
('C005','Gabriela','Paredes Vega','69874523','943210987','gabi.paredes@gmail.com','2024-04-01'),
('C006','Andrés','Huamán Ccori','77654321','932109876','andres.huaman@gmail.com','2024-04-15'),
('C007','Sofía','Vargas Ibáñez','71234567','921098765','sofia.vargas@yahoo.com','2024-05-03'),
('C008','Martín','Castillo Ponce','68901234','910987654','martin.castillo@gmail.com','2024-05-18'),
('C009','Natalia','Espinoza Rojas','73456789','909876543','natalia.espinoza@gmail.com','2024-06-07'),
('C010','Rodrigo','Benítez Cárdenas','76543210','998877665','rodrigo.benitez@hotmail.com','2024-06-20');

INSERT INTO tematica (id_tematica, descripcion, precio_base, estado) VALUES
('T001', 'Cumpleaños temático de princesas',        800.00,  'Disponible'),
('T002', 'Fiesta de superhéroes para niños',        750.00,  'Disponible'),
('T003', 'Cumpleaños tropical / Luau',               950.00,  'Disponible'),
('T004', 'Fiesta de quinceañera elegante',          2000.00,  'Disponible'),
('T005', 'Celebración de aniversario romántico',    1200.00,  'Disponible'),
('T006', 'Cumpleaños temático de dinosaurios',       700.00,  'Disponible'),
('T007', 'Fiesta de Halloween infantil',             850.00,  'Disponible'),
('T008', 'Baby shower decoración bosque',            600.00,  'Disponible'),
('T009', 'Cumpleaños temático espacial',             780.00,  'Disponible'),
('T010', 'Fiesta de graduación universitaria',      1500.00,  'Disponible');

INSERT INTO reserva (id_reserva, fecha_reserva, fecha_evento, hora_inicio, hora_fin, direccion, edad_cumpleanero, observaciones, estado, id_cliente, id_tematica) VALUES
('R001', '2026-06-25', '2026-07-10', '15:00', '19:00', 'Salón Fantasía, Miraflores',        6,    'Alérgica al maní',              'Confirmada', 'C001', 'T001'),
('R002', '2026-06-27', '2026-07-15', '14:00', '18:00', 'Salón El Castillo, Surco',          8,    'Solicita decoración extra',      'Confirmada', 'C002', 'T002'),
('R003', '2026-07-01', '2026-07-20', '16:00', '21:00', 'Club Playa Azul, Chorrillos',       NULL, 'Evento para adultos',            'Confirmada', 'C003', 'T003'),
('R004', '2027-07-05', '2027-07-25', '19:00', '23:59', 'Gran Salón Royal, San Isidro',      15,   'Mesa de honor para 10 personas', 'Confirmada', 'C004', 'T004'),
('R005', '2027-07-08', '2027-08-02', '19:30', '23:00', 'Restaurante Vista, Barranco',       NULL, 'Aniversario 10 años',            'Pendiente',  'C005', 'T005'),
('R006', '2026-07-10', '2026-08-08', '15:00', '19:00', 'Salón Aventura, Los Olivos',        5,    'Temática con piñata incluida',   'Confirmada', 'C006', 'T006'),
('R007', '2027-09-15', '2027-10-31', '16:00', '20:00', 'Salón Encantado, San Borja',        7,    'Disfraces para invitados',       'Pendiente',  'C007', 'T007'),
('R008', '2026-07-30', '2026-08-20', '11:00', '15:00', 'Salón Jardín, La Molina',           NULL, 'Primer bebé, gemelos',           'Confirmada', 'C008', 'T008'),
('R009', '2026-08-20', '2026-09-05', '15:00', '19:00', 'Salón Galaxia, Pueblo Libre',       10,   'Torta temática de cohetes',      'Confirmada', 'C009', 'T009'),
('R010', '2027-08-25', '2027-09-15', '19:00', '23:59', 'Centro Conv. Lima, Cercado',        NULL, 'Graduación de Ingeniería',       'Pendiente',  'C010', 'T010'),
('R011', '2027-10-25', '2027-11-15', '19:00', '23:59', 'Auditorio San Marcos, Cercado',     NULL, 'Graduación de Enfermería',       'Confirmada', 'C003', 'T010');

INSERT INTO servicio_adicional (id_servicio_adicional, nombre_servicio_adicional, descripcion, precio, estado, id_reserva) VALUES
('S001', 'Fotografía profesional', 'Cobertura completa del evento con edición',         350.00, 'Activo', 'R004'),
('S002', 'Animación infantil',     'Payaso y juegos para niños por 2 horas',            200.00, 'Activo', 'R006'),
('S003', 'DJ y sonido',            'Equipo de sonido profesional + DJ por 4h',          450.00, 'Activo', 'R010'),
('S004', 'Torta personalizada',    'Torta de 4 pisos con diseño temático',              300.00, 'Activo', 'R001'),
('S005', 'Decoración floral',      'Arreglos florales para mesa y entrada',             250.00, 'Activo', 'R011'),
('S006', 'Piñata temática',        'Piñata personalizada con relleno incluido',         120.00, 'Activo', 'R002'),
('S007', 'Pintacaritas',           'Diseños faciales artísticos para niños asistentes', 180.00, 'Activo', 'R009'),
('S008', 'Catering buffet',        'Servicio de buffet para 30 personas',               800.00, 'Activo', 'R008'),
('S009', 'Video profesional',      'Grabación y edición de video del evento',           400.00, 'Activo', 'R003'),
('S010', 'Photobooth',             'Cabina de fotos con accesorios temáticos',          220.00, 'Activo', 'R007'),
('S011', 'Coordinación de evento', 'Personal de apoyo para logística',                  150.00, 'Activo', 'R005');

INSERT INTO pago (id_pago, fecha_pago, monto_total, metodo_pago, estado_pago, total_cuotas, id_reserva) VALUES
('P001', '2026-06-25', 1100.00, 'YAPE',           'Pagado',          1, 'R001'),
('P002', '2026-06-27',  870.00, 'PLIN',           'Pagado',          2, 'R002'),
('P003', '2026-07-01', 1350.00, 'TRANSFERENCIA',  'Pagado',          1, 'R003'),
('P004', '2027-07-05', 2350.00, 'EFECTIVO',       'Pago parcial',    3, 'R004'),
('P005', '2027-07-08', 1350.00, 'TARJETA',        'Pendiente',       2, 'R005'),
('P006', '2026-07-10',  900.00, 'TRANSFERENCIA',  'Pagado',          1, 'R006'),
('P007', '2027-09-15', 1070.00, 'TARJETA',        'Pendiente',       2, 'R007'),
('P008', '2026-07-30', 1400.00, 'YAPE',           'Pagado',          1, 'R008'),
('P009', '2026-08-20',  960.00, 'TRANSFERENCIA',  'Pago parcial',    2, 'R009'),
('P010', '2027-08-25', 1950.00, 'EFECTIVO',       'Pendiente',       3, 'R010'),
('P011', '2027-10-25', 1750.00, 'YAPE',           'Pendiente',       1, 'R011');

INSERT INTO cuota (id_cuota, numero_cuota, monto, fecha_vencimiento, fecha_pago, estado, id_pago) VALUES
('Q001',  1, 1100.00, '2026-06-25', '2026-06-25',  'Pagada',    'P001'),
('Q002',  1,  435.00, '2026-06-27', '2026-06-27',  'Pagada',    'P002'),
('Q003',  2,  435.00, '2026-07-27', '2026-07-27',  'Pagada',    'P002'),
('Q004',  1, 1350.00, '2026-07-01', '2026-07-01',  'Pagada',    'P003'),
('Q005',  1,  783.33, '2027-07-05', '2027-07-10',  'Pagada',    'P004'),
('Q006',  2,  783.33, '2027-08-05', NULL,          'Pendiente', 'P004'),
('Q007',  3,  783.34, '2027-09-05', NULL,          'Pendiente', 'P004'),
('Q008',  1,  675.00, '2027-07-08', NULL,          'Pendiente', 'P005'),
('Q009',  2,  675.00, '2027-08-08', NULL,          'Pendiente', 'P005'),
('Q010',  1,  900.00, '2026-07-10', '2026-07-10',  'Pagada',    'P006'),
('Q011',  1,  535.00, '2027-09-15', NULL,          'Pendiente', 'P007'),
('Q012',  2,  535.00, '2027-10-15', NULL,          'Pendiente', 'P007'),
('Q013',  1, 1400.00, '2026-07-30', '2026-07-30',  'Pagada',    'P008'),
('Q014',  1,  480.00, '2026-08-20', '2026-08-20',  'Pagada',    'P009'),
('Q015',  2,  480.00, '2026-09-20', NULL,          'Pendiente', 'P009'),
('Q016',  1,  650.00, '2027-08-25', NULL,          'Pendiente', 'P010'),
('Q017',  2,  650.00, '2027-09-25', NULL,          'Pendiente', 'P010'),
('Q018',  3,  650.00, '2027-10-25', NULL,          'Pendiente', 'P010'),
('Q019',  1, 1750.00, '2027-10-25', NULL,          'Pendiente', 'P011');

-- =============================================
-- VERIFICAR
-- =============================================
SELECT 'cliente'            AS tabla, COUNT(*) AS registros FROM cliente
UNION ALL
SELECT 'tematica'           AS tabla, COUNT(*) AS registros FROM tematica
UNION ALL
SELECT 'reserva'            AS tabla, COUNT(*) AS registros FROM reserva
UNION ALL
SELECT 'servicio_adicional' AS tabla, COUNT(*) AS registros FROM servicio_adicional
UNION ALL
SELECT 'pago'               AS tabla, COUNT(*) AS registros FROM pago
UNION ALL
SELECT 'cuota'               AS tabla, COUNT(*) AS registros FROM cuota;

SELECT * FROM cliente
```