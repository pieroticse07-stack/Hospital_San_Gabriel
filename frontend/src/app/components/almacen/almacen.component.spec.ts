import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { AlmacenService } from '../../services/almacen.service';
import { AlmacenComponent } from './almacen.component';

describe('AlmacenComponent', () => {
  let fixture: ComponentFixture<AlmacenComponent>;

  beforeEach(async () => {
    const almacenService = {
      categorias: () => of([]),
      productos: () => of([]),
      entradas: () => of([]),
      crearCategoria: () => of({}),
      crearProducto: () => of({}),
      actualizarProducto: () => of({}),
      desactivarProducto: () => of(undefined),
      registrarEntrada: () => of({})
    };

    await TestBed.configureTestingModule({
      imports: [AlmacenComponent],
      providers: [{ provide: AlmacenService, useValue: almacenService }]
    }).compileComponents();

    fixture = TestBed.createComponent(AlmacenComponent);
    fixture.detectChanges();
  });

  it('muestra los accesos a productos, categorías y entradas', () => {
    const labels = Array.from(fixture.nativeElement.querySelectorAll('.section-tab'))
      .map((button: Element) => button.textContent?.trim());

    expect(labels).toEqual(['Productos', 'Categorías', 'Registro de entradas']);
  });

  it('abre la sección de categorías al seleccionarla', () => {
    const buttons = fixture.nativeElement.querySelectorAll('.section-tab');
    buttons[1].click();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Registrar categoría');
  });
});
