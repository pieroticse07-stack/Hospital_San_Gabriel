import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { PrimerComponenteComponent } from './primer-componente.component';

describe('PrimerComponenteComponent', () => {
  let component: PrimerComponenteComponent;
  let fixture: ComponentFixture<PrimerComponenteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PrimerComponenteComponent],
      providers: [provideHttpClient()]
    }).compileComponents();

    fixture = TestBed.createComponent(PrimerComponenteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
