/* Hospital San Gabriel - módulo de almacén. Ejecutar en una base de datos vacía. */
IF DB_ID(N'HospitalSanGabriel') IS NULL CREATE DATABASE HospitalSanGabriel;
GO
USE HospitalSanGabriel;
GO

IF OBJECT_ID(N'dbo.Categorias', N'U') IS NULL
CREATE TABLE dbo.Categorias (
  CategoriaID int IDENTITY(1,1) CONSTRAINT PK_Categorias PRIMARY KEY,
  Nombre nvarchar(80) NOT NULL CONSTRAINT UQ_Categorias_Nombre UNIQUE,
  Descripcion nvarchar(250) NULL,
  Estado bit NOT NULL CONSTRAINT DF_Categorias_Estado DEFAULT 1,
  FechaCreacion datetime2(0) NOT NULL CONSTRAINT DF_Categorias_Fecha DEFAULT SYSUTCDATETIME()
);
GO
IF OBJECT_ID(N'dbo.Productos', N'U') IS NULL
CREATE TABLE dbo.Productos (
  ProductoID int IDENTITY(1,1) CONSTRAINT PK_Productos PRIMARY KEY,
  Codigo nvarchar(30) NOT NULL CONSTRAINT UQ_Productos_Codigo UNIQUE,
  Nombre nvarchar(120) NOT NULL,
  Descripcion nvarchar(500) NULL,
  CategoriaID int NOT NULL,
  PrecioUnitario decimal(12,2) NOT NULL,
  StockMinimo int NOT NULL,
  Estado bit NOT NULL CONSTRAINT DF_Productos_Estado DEFAULT 1,
  FechaCreacion datetime2(0) NOT NULL CONSTRAINT DF_Productos_Fecha DEFAULT SYSUTCDATETIME(),
  CONSTRAINT FK_Productos_Categorias FOREIGN KEY (CategoriaID) REFERENCES dbo.Categorias(CategoriaID),
  CONSTRAINT CK_Productos_Precio CHECK (PrecioUnitario > 0),
  CONSTRAINT CK_Productos_StockMinimo CHECK (StockMinimo > 0)
);
GO
IF OBJECT_ID(N'dbo.Lotes', N'U') IS NULL
CREATE TABLE dbo.Lotes (
  LoteID int IDENTITY(1,1) CONSTRAINT PK_Lotes PRIMARY KEY,
  ProductoID int NOT NULL,
  NumeroLote nvarchar(50) NOT NULL,
  FechaVencimiento date NOT NULL,
  CantidadDisponible int NOT NULL,
  FechaIngreso datetime2(0) NOT NULL CONSTRAINT DF_Lotes_Fecha DEFAULT SYSUTCDATETIME(),
  CONSTRAINT FK_Lotes_Productos FOREIGN KEY (ProductoID) REFERENCES dbo.Productos(ProductoID),
  CONSTRAINT CK_Lotes_Cantidad CHECK (CantidadDisponible >= 0),
  CONSTRAINT UQ_Lotes_Producto_Numero UNIQUE (ProductoID, NumeroLote)
);
GO
IF OBJECT_ID(N'dbo.HistorialMovimientos', N'U') IS NULL
CREATE TABLE dbo.HistorialMovimientos (
  MovimientoID bigint IDENTITY(1,1) CONSTRAINT PK_HistorialMovimientos PRIMARY KEY,
  ProductoID int NOT NULL,
  LoteID int NULL,
  TipoMovimiento varchar(10) NOT NULL,
  Cantidad int NOT NULL,
  Motivo varchar(20) NOT NULL,
  NumeroLote nvarchar(50) NULL,
  FechaVencimiento date NULL,
  FechaMovimiento datetime2(0) NOT NULL CONSTRAINT DF_Historial_Fecha DEFAULT SYSUTCDATETIME(),
  Observacion nvarchar(500) NULL,
  CONSTRAINT FK_Historial_Productos FOREIGN KEY (ProductoID) REFERENCES dbo.Productos(ProductoID),
  CONSTRAINT FK_Historial_Lotes FOREIGN KEY (LoteID) REFERENCES dbo.Lotes(LoteID),
  CONSTRAINT CK_Historial_Cantidad CHECK (Cantidad > 0),
  CONSTRAINT CK_Historial_Tipo CHECK (TipoMovimiento IN ('ENTRADA','SALIDA')),
  CONSTRAINT CK_Historial_Motivo CHECK (Motivo IN ('compras','donaciones','devoluciones'))
);
GO

IF NOT EXISTS(SELECT 1 FROM dbo.Categorias)
INSERT dbo.Categorias(Nombre, Descripcion) VALUES
 (N'Medicamentos',N'Medicamentos y productos farmacéuticos'),
 (N'Material médico',N'Insumos y material médico descartable'),
 (N'Laboratorio',N'Reactivos e insumos de laboratorio'),
 (N'Limpieza hospitalaria',N'Productos para limpieza y desinfección');
GO

CREATE OR ALTER PROCEDURE dbo.usp_Categoria_Crear @Nombre nvarchar(80), @Descripcion nvarchar(250)=NULL AS
BEGIN
 SET NOCOUNT ON; SET XACT_ABORT ON;
 BEGIN TRY
  BEGIN TRANSACTION;
  INSERT dbo.Categorias(Nombre,Descripcion) VALUES(LTRIM(RTRIM(@Nombre)),@Descripcion);
  DECLARE @id int=SCOPE_IDENTITY();
  SELECT CategoriaID categoria_id,Nombre nombre,Descripcion descripcion,Estado estado FROM dbo.Categorias WHERE CategoriaID=@id;
  COMMIT TRANSACTION;
 END TRY BEGIN CATCH IF XACT_STATE()<>0 ROLLBACK TRANSACTION; THROW; END CATCH
END;
GO
CREATE OR ALTER PROCEDURE dbo.usp_Producto_Crear
 @Codigo nvarchar(30),@Nombre nvarchar(120),@Descripcion nvarchar(500)=NULL,@CategoriaID int,@PrecioUnitario decimal(12,2),@StockMinimo int AS
BEGIN
 SET NOCOUNT ON; SET XACT_ABORT ON;
 BEGIN TRY
  BEGIN TRANSACTION;
  IF @PrecioUnitario<=0 OR @StockMinimo<=0 THROW 50001,'Precio y stock mínimo deben ser mayores a cero.',1;
  IF NOT EXISTS(SELECT 1 FROM dbo.Categorias WHERE CategoriaID=@CategoriaID AND Estado=1) THROW 50002,'La categoría no existe o está inactiva.',1;
  INSERT dbo.Productos(Codigo,Nombre,Descripcion,CategoriaID,PrecioUnitario,StockMinimo) VALUES(@Codigo,@Nombre,@Descripcion,@CategoriaID,@PrecioUnitario,@StockMinimo);
  DECLARE @id int=SCOPE_IDENTITY();
  SELECT p.ProductoID producto_id,p.Codigo codigo,p.Nombre nombre,p.Descripcion descripcion,p.CategoriaID categoria_id,c.Nombre categoria_nombre,p.PrecioUnitario precio_unitario,p.StockMinimo stock_minimo,p.Estado estado,0 stock_actual FROM dbo.Productos p JOIN dbo.Categorias c ON c.CategoriaID=p.CategoriaID WHERE p.ProductoID=@id;
  COMMIT TRANSACTION;
 END TRY BEGIN CATCH IF XACT_STATE()<>0 ROLLBACK TRANSACTION; THROW; END CATCH
END;
GO
CREATE OR ALTER PROCEDURE dbo.usp_Producto_Actualizar
 @ProductoID int,@Codigo nvarchar(30),@Nombre nvarchar(120),@Descripcion nvarchar(500)=NULL,@CategoriaID int,@PrecioUnitario decimal(12,2),@StockMinimo int AS
BEGIN
 SET NOCOUNT ON; SET XACT_ABORT ON;
 BEGIN TRY
  BEGIN TRANSACTION;
  IF @PrecioUnitario<=0 OR @StockMinimo<=0 THROW 50001,'Precio y stock mínimo deben ser mayores a cero.',1;
  IF NOT EXISTS(SELECT 1 FROM dbo.Categorias WHERE CategoriaID=@CategoriaID AND Estado=1) THROW 50002,'La categoría no existe o está inactiva.',1;
  UPDATE dbo.Productos SET Codigo=@Codigo,Nombre=@Nombre,Descripcion=@Descripcion,CategoriaID=@CategoriaID,PrecioUnitario=@PrecioUnitario,StockMinimo=@StockMinimo WHERE ProductoID=@ProductoID AND Estado=1;
  IF @@ROWCOUNT=0 THROW 50003,'Producto inexistente o inactivo.',1;
  SELECT p.ProductoID producto_id,p.Codigo codigo,p.Nombre nombre,p.Descripcion descripcion,p.CategoriaID categoria_id,c.Nombre categoria_nombre,p.PrecioUnitario precio_unitario,p.StockMinimo stock_minimo,p.Estado estado,COALESCE((SELECT SUM(CantidadDisponible) FROM dbo.Lotes WHERE ProductoID=p.ProductoID),0) stock_actual FROM dbo.Productos p JOIN dbo.Categorias c ON c.CategoriaID=p.CategoriaID WHERE p.ProductoID=@ProductoID;
  COMMIT TRANSACTION;
 END TRY BEGIN CATCH IF XACT_STATE()<>0 ROLLBACK TRANSACTION; THROW; END CATCH
END;
GO
CREATE OR ALTER PROCEDURE dbo.usp_Producto_Desactivar @ProductoID int AS
BEGIN
 SET NOCOUNT ON; SET XACT_ABORT ON;
 BEGIN TRY
  BEGIN TRANSACTION;
  UPDATE dbo.Productos SET Estado=0 WHERE ProductoID=@ProductoID AND Estado=1;
  IF @@ROWCOUNT=0 THROW 50003,'Producto inexistente o ya inactivo.',1;
  SELECT @ProductoID producto_id;
  COMMIT TRANSACTION;
 END TRY BEGIN CATCH IF XACT_STATE()<>0 ROLLBACK TRANSACTION; THROW; END CATCH
END;
GO
CREATE OR ALTER PROCEDURE dbo.usp_Entrada_Registrar
 @ProductoID int,@Cantidad int,@Motivo varchar(20),@NumeroLote nvarchar(50),@FechaVencimiento date,@Observacion nvarchar(500)=NULL AS
BEGIN
 SET NOCOUNT ON; SET XACT_ABORT ON;
 BEGIN TRY
  BEGIN TRANSACTION;
  IF @Cantidad<=0 THROW 50004,'La cantidad debe ser mayor a cero.',1;
  IF @Motivo NOT IN ('compras','donaciones','devoluciones') THROW 50005,'Motivo de entrada inválido.',1;
  IF @FechaVencimiento<=CONVERT(date,GETDATE()) THROW 50006,'La fecha de vencimiento debe ser futura.',1;
  IF NOT EXISTS(SELECT 1 FROM dbo.Productos WITH (UPDLOCK,HOLDLOCK) WHERE ProductoID=@ProductoID AND Estado=1) THROW 50003,'Producto inexistente o inactivo.',1;
  DECLARE @lote int;
  SELECT @lote=LoteID FROM dbo.Lotes WITH (UPDLOCK,HOLDLOCK) WHERE ProductoID=@ProductoID AND NumeroLote=@NumeroLote;
  IF @lote IS NULL
  BEGIN
   INSERT dbo.Lotes(ProductoID,NumeroLote,FechaVencimiento,CantidadDisponible) VALUES(@ProductoID,@NumeroLote,@FechaVencimiento,@Cantidad);
   SET @lote=SCOPE_IDENTITY();
  END
  ELSE
  BEGIN
   IF EXISTS(SELECT 1 FROM dbo.Lotes WHERE LoteID=@lote AND FechaVencimiento<>@FechaVencimiento) THROW 50007,'El número de lote ya existe con otra fecha de vencimiento.',1;
   UPDATE dbo.Lotes SET CantidadDisponible=CantidadDisponible+@Cantidad WHERE LoteID=@lote;
  END;
  INSERT dbo.HistorialMovimientos(ProductoID,LoteID,TipoMovimiento,Cantidad,Motivo,NumeroLote,FechaVencimiento,Observacion)
  VALUES(@ProductoID,@lote,'ENTRADA',@Cantidad,@Motivo,@NumeroLote,@FechaVencimiento,@Observacion);
  DECLARE @mov bigint=SCOPE_IDENTITY();
  SELECT h.MovimientoID movimiento_id,h.ProductoID producto_id,p.Nombre producto_nombre,h.Cantidad cantidad,h.Motivo motivo,h.NumeroLote numero_lote,h.FechaVencimiento fecha_vencimiento,CAST(h.FechaMovimiento AS date) fecha_movimiento,h.Observacion observacion FROM dbo.HistorialMovimientos h JOIN dbo.Productos p ON p.ProductoID=h.ProductoID WHERE h.MovimientoID=@mov;
  COMMIT TRANSACTION;
 END TRY BEGIN CATCH IF XACT_STATE()<>0 ROLLBACK TRANSACTION; THROW; END CATCH
END;
GO
